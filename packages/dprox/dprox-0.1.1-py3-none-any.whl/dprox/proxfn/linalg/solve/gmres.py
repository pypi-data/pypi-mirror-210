# ported from https://github.com/xitorch/xitorch/blob/master/xitorch/_impls/linalg/solve.py

import numpy as np
import torch
from scipy.sparse.linalg import gmres as scipy_gmres


def scipy_gmres(A, B, min_eps=1e-9, max_niter=None, **unused):
    """
    Using SciPy's gmres method to solve the linear equation.

    Keyword arguments
    -----------------
    min_eps: float
        Relative tolerance for stopping conditions
    max_niter: int or None
        Maximum number of iterations. If ``None``, default to twice of the
        number of columns of ``A``.
    """
    # A: (*BA, nr, nr)
    # B: (*BB, nr, ncols)
    # E: (*BE, ncols) or None
    # M: (*BM, nr, nr) or None

    # NOTE: currently only works for batched B (1 batch dim), but unbatched A
    assert len(A.shape) == 2 and len(B.shape) == 3, "Currently only works for batched B (1 batch dim), but unbatched A"
    assert not torch.is_complex(B), "complex is not supported in gmres"

    # check the parameters
    msg = "GMRES can only do AX=B"
    assert A.shape[-2] == A.shape[-1], "GMRES can only work for square operator for now"
    
    nbatch, na, ncols = B.shape
    if max_niter is None:
        max_niter = 2 * na

    B = B.transpose(-1, -2)  # (nbatch, ncols, na)

    # convert the numpy/scipy
    op = A.scipy_linalg_op()
    B_np = B.detach().cpu().numpy()
    res_np = np.empty(B.shape, dtype=get_np_dtype(B.dtype))
    for i in range(nbatch):
        for j in range(ncols):
            x, info = scipy_gmres(op, B_np[i, j, :], tol=min_eps, atol=1e-12, maxiter=max_niter)
            if info > 0:
                msg = "The GMRES iteration does not converge to the desired value "\
                      "(%.3e) after %d iterations" % \
                      (min_eps, info)
                warnings.warn(ConvergenceWarning(msg))
            res_np[i, j, :] = x

    res = torch.tensor(res_np, dtype=B.dtype, device=B.device)
    res = res.transpose(-1, -2)  # (nbatch, na, ncols)
    return res


def gmres(A: LinearOperator, B: torch.Tensor,
          E: Optional[torch.Tensor] = None,
          M: Optional[LinearOperator] = None,
          posdef: Optional[bool] = None,
          max_niter: Optional[int] = None,
          rtol: float = 1e-6,
          atol: float = 1e-8,
          eps: float = 1e-12,
          **unused) -> torch.Tensor:
    r"""
    Solve the linear equations using Generalised minial residual method.

    Keyword arguments
    -----------------
    posdef: bool or None
        Indicating if the operation :math:`\mathbf{AX-MXE}` a positive
        definite for all columns and batches.
        If None, it will be determined by power iterations.
    max_niter: int or None
        Maximum number of iteration. If None, it is set to ``int(1.5 * A.shape[-1])``
    rtol: float
        Relative tolerance for stopping condition w.r.t. norm of B
    atol: float
        Absolute tolerance for stopping condition w.r.t. norm of B
    eps: float
        Substitute the absolute zero in the algorithm's denominator with this
        value to avoid nan.
    """
    converge = False

    nr, ncols = A.shape[-1], B.shape[-1]
    if max_niter is None:
        max_niter = int(nr)

    # if B is all zeros, then return zeros
    batchdims = _get_batchdims(A, B, E, M)
    if torch.allclose(B, B * 0, rtol=rtol, atol=atol):
        x0 = torch.zeros((*batchdims, nr, ncols), dtype=A.dtype, device=A.device)
        return x0

    # setup the preconditioning and the matrix problem
    need_hermit = False
    A_fcn, AT_fcn, B2, col_swapped = _setup_linear_problem(A, B, E, M, batchdims,
                                                           posdef, need_hermit)

    # get the stopping matrix
    B_norm = B2.norm(dim=-2, keepdim=True)  # (*BB, 1, nc)
    stop_matrix = torch.max(rtol * B_norm, atol * torch.ones_like(B_norm))  # (*BB, 1, nc)

    # prepare the initial guess (it's just all zeros)
    x0shape = (ncols, *batchdims, nr, 1) if col_swapped else (*batchdims, nr, ncols)
    x0 = torch.zeros(x0shape, dtype=A.dtype, device=A.device)

    r = B2 - A_fcn(x0)  # torch.Size([*batch_dims, nr, ncols])
    best_resid = r.norm(dim=-2, keepdim=True)  # / B_norm

    best_resid = best_resid.max().item()
    best_res = x0
    q = torch.empty([max_niter] + list(r.shape), dtype=A.dtype, device=A.device)
    q[0] = r / _safedenom(r.norm(dim=-2, keepdim=True), eps)  # torch.Size([*batch_dims, nr, ncols])
    h = torch.zeros((*batchdims, ncols, max_niter + 1, max_niter), dtype=A.dtype, device=A.device)
    h = h.reshape((-1, ncols, max_niter + 1, max_niter))

    for k in range(min(nr, max_niter)):
        y = A_fcn(q[k])  # torch.Size([*batch_dims, nr, ncols])
        for j in range(k + 1):
            h[..., j, k] = _dot(q[j], y).reshape(-1, ncols)
            y = y - h[..., j, k].reshape(*batchdims, 1, ncols) * q[j]

        h[..., k + 1, k] = torch.linalg.norm(y, dim=-2)
        if torch.any(h[..., k + 1, k]) != 0 and k != max_niter - 1:
            q[k + 1] = y.reshape(-1, nr, ncols) / h[..., k + 1, k].reshape(-1, 1, ncols)
            q[k + 1] = q[k + 1].reshape(*batchdims, nr, ncols)

        b = torch.zeros((*batchdims, ncols, k + 1), dtype=A.dtype, device=A.device)
        b = b.reshape(-1, ncols, k + 1)
        b[..., 0] = torch.linalg.norm(r, dim=-2)
        rk = torch.linalg.lstsq(h[..., :k + 1, :k], b)[0]  # torch.Size([*batch_dims, max_niter])
        # Q, R = torch.linalg.qr(h[:, :k+1, :k], mode='complete')
        # result = torch.triangular_solve(torch.matmul(Q.permute(0, 2, 1), b[:, :, None])[:, :-1], R[:, :-1, :])[0]

        res = torch.empty([])
        for i in range(k):
            res = res + q[i] * rk[..., i].reshape(*batchdims, 1, ncols) + x0 if res.size() \
                else q[i] * rk[..., i].reshape(*batchdims, 1, ncols) + x0
            # res = res * B_norm

        if res.size():
            resid = B2 - A_fcn(res)
            resid_norm = resid.norm(dim=-2, keepdim=True)

            # save the best results
            max_resid_norm = resid_norm.max().item()
            if max_resid_norm < best_resid:
                best_resid = max_resid_norm
                best_res = res

            if torch.all(resid_norm < stop_matrix):
                converge = True
                break

    if not converge:
        msg = ("Convergence is not achieved after %d iterations. "
               "Max norm of resid: %.3e") % (max_niter, best_resid)
        warnings.warn(ConvergenceWarning(msg))

    res = best_res
    return res