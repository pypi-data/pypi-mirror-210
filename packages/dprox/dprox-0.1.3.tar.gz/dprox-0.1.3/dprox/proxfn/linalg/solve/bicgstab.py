import torch

def bicgstab(A: LinearOperator, B: torch.Tensor,
             E: Optional[torch.Tensor] = None,
             M: Optional[LinearOperator] = None,
             posdef: Optional[bool] = None,
             precond_l: Optional[LinearOperator] = None,
             precond_r: Optional[LinearOperator] = None,
             max_niter: Optional[int] = None,
             rtol: float = 1e-6,
             atol: float = 1e-8,
             eps: float = 1e-12,
             verbose: bool = False,
             resid_calc_every: int = 10,
             **unused) -> torch.Tensor:
    r"""
    Solve the linear equations using stabilized Biconjugate-Gradient method.

    Keyword arguments
    -----------------
    posdef: bool or None
        Indicating if the operation :math:`\mathbf{AX-MXE}` a positive
        definite for all columns and batches.
        If None, it will be determined by power iterations.
    precond_l: LinearOperator or None
        LinearOperator for the left preconditioning. If None, no
        preconditioner is applied.
    precond_r: LinearOperator or None
        LinearOperator for the right preconditioning. If None, no
        preconditioner is applied.
    max_niter: int or None
        Maximum number of iteration. If None, it is set to ``int(1.5 * A.shape[-1])``
    rtol: float
        Relative tolerance for stopping condition w.r.t. norm of B
    atol: float
        Absolute tolerance for stopping condition w.r.t. norm of B
    eps: float
        Substitute the absolute zero in the algorithm's denominator with this
        value to avoid nan.
    resid_calc_every: int
        Calculate the residual in its actual form instead of substitution form
        with this frequency, to avoid rounding error accummulation.
        If your linear operator has bad numerical precision, set this to be low.
        If 0, then never calculate the residual in its actual form.
    verbose: bool
        Verbosity of the algorithm.
    """
    nr, ncols = B.shape[-2:]
    if max_niter is None:
        max_niter = int(1.5 * nr)

    # if B is all zeros, then return zeros
    batchdims = _get_batchdims(A, B, E, M)
    if torch.allclose(B, B * 0, rtol=rtol, atol=atol):
        x0 = torch.zeros((*batchdims, nr, ncols), dtype=A.dtype, device=A.device)
        return x0

    # setup the preconditioning and the matrix problem
    precond_fcn_l = _setup_precond(precond_l)
    precond_fcn_r = _setup_precond(precond_r)
    need_hermit = False
    A_fcn, AT_fcn, B2, col_swapped = _setup_linear_problem(A, B, E, M, batchdims,
                                                           posdef, need_hermit)

    # get the stopping matrix
    B_norm = B2.norm(dim=-2, keepdim=True)  # (*BB, 1, nc)
    stop_matrix = torch.max(rtol * B_norm, atol * torch.ones_like(B_norm))  # (*BB, 1, nc)

    # prepare the initial guess (it's just all zeros)
    x0shape = (ncols, *batchdims, nr, 1) if col_swapped else (*batchdims, nr, ncols)
    xk = torch.zeros(x0shape, dtype=A.dtype, device=A.device)

    rk = B2 - A_fcn(xk)
    r0hat = rk
    rho_k = _dot(r0hat, rk)
    omega_k = torch.tensor(1.0, dtype=A.dtype, device=A.device)
    alpha: Union[float, torch.Tensor] = 1.0
    vk: Union[float, torch.Tensor] = 0.0
    pk: Union[float, torch.Tensor] = 0.0
    converge = False
    best_resid = rk.norm(dim=-2).max()
    best_xk = xk
    for k in range(1, max_niter + 1):
        rho_knew = _dot(r0hat, rk)
        omega_denom = _safedenom(omega_k, eps)
        beta = rho_knew / _safedenom(rho_k, eps) * (alpha / omega_denom)
        pk = rk + beta * (pk - omega_k * vk)
        y = precond_fcn_r(pk)
        vk = A_fcn(y)
        alpha = rho_knew / _safedenom(_dot(r0hat, vk), eps)
        h = xk + alpha * y

        s = rk - alpha * vk
        z = precond_fcn_r(s)
        t = A_fcn(z)
        Kt = precond_fcn_l(t)
        omega_k = _dot(Kt, precond_fcn_l(s)) / _safedenom(_dot(Kt, Kt), eps)
        xk = h + omega_k * z

        # correct the residual calculation regularly
        if resid_calc_every != 0 and k % resid_calc_every == 0:
            rk = B2 - A_fcn(xk)
        else:
            rk = s - omega_k * t

        # calculate the residual
        resid = rk
        resid_norm = resid.norm(dim=-2, keepdim=True)

        # save the best results
        max_resid_norm = resid_norm.max().item()
        if max_resid_norm < best_resid:
            best_resid = max_resid_norm
            best_xk = xk

        if verbose:
            if k < 10 or k % 10 == 0:
                print("%4d: |dy|=%.3e" % (k, resid_norm))

        # check for the stopping conditions
        if torch.all(resid_norm < stop_matrix):
            converge = True
            break

        rho_k = rho_knew

    xk = best_xk
    if not converge:
        msg = ("Convergence is not achieved after %d iterations. "
               "Max norm of resid: %.3e") % (max_niter, best_resid)
        warnings.warn(ConvergenceWarning(msg))
    if col_swapped:
        # x: (ncols, *, nr, 1)
        xk = xk.transpose(0, -1).squeeze(0)  # (*, nr, ncols)
    return xk
