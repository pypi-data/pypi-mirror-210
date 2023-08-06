@functools.wraps(broyden1)
def broyden1_solve(A, B, E=None, M=None, **options):
    return _rootfinder_solve("broyden1", A, B, E, M, **options)

def _rootfinder_solve(alg, A, B, E=None, M=None, **options):
    # using rootfinder algorithm
    nr = A.shape[-1]
    ncols = B.shape[-1]

    # set up the function for the rootfinding
    def fcn_rootfinder(xi):
        # xi: (*BX, nr*ncols)
        x = xi.reshape(*xi.shape[:-1], nr, ncols)  # (*BX, nr, ncols)
        y = A.mm(x) - B  # (*BX, nr, ncols)
        if E is not None:
            MX = M.mm(x) if M is not None else x
            MXE = MX * E.unsqueeze(-2)
            y = y - MXE  # (*BX, nr, ncols)
        y = y.reshape(*xi.shape[:-1], -1)  # (*BX, nr*ncols)
        return y

    # setup the initial guess (the batch dimension must be the largest)
    batchdims = _get_batchdims(A, B, E, M)
    x0 = torch.zeros((*batchdims, nr * ncols), dtype=A.dtype, device=A.device)

    if alg == "broyden1":
        x = broyden1(fcn_rootfinder, x0, **options)
    else:
        raise RuntimeError("Unknown method %s" % alg)
    x = x.reshape(*x.shape[:-1], nr, ncols)
    return x
