from ._models import mc, mc_t
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt
from logging import warning
from ._example_data import return_data
import pandas as pd
from itertools import product
from tqdm.auto import tqdm
from scipy.special import loggamma
from scipy.integrate import quad, simpson


class Nunchaku:
    """Find how many linear segments a dataset should be divide into,
    and find the start and end of each linear segment.

    Parameters
    ----------
    X : list of floats or 1-D numpy array
        the x vector of data, sorted ascendingly.
    Y : array-like
        the y vector or matrix of data, each row being one replicate of
        measurement.
    err : list of floats or 1-D numpy array, optional
        the error of the input data.
    yrange : list of length 2, optional
        the min and max of y allowed by the instrument's readout.
    prior : list of length 2 or 4, optional
        the prior range of the gradient (and the intercept when length is 4).
        This argument will overwrite `yrange`.
    estimate_err : bool, optional
        if True, estimate error from data; default True when Y has >= 3
        replicates.
    minlen : int, default 3
        the minimal length of a valid segment (must be >= 3).
    method : {"simpson", "quad"}, default "simpson"
        the numerical integration method to be used when error is neither
        estimated nor provided.

    Raises
    ------
    ValueError
        when Y has multiple replicates and err is provided.

    ValueError
        when the length of `prior` is not 2 or 4, if provided.

    Examples
    --------
    >>> from nunchaku import Nunchaku, get_example_data
    >>> x, y = get_example_data()
    >>> nc = Nunchaku(x, y, prior=[-5,5]) # load data and set prior of gradient
    >>> # compare models with 1, 2, 3 and 4 linear segments
    >>> numseg, evidences = nc.get_number(max_num=4)
    >>> # get the mean and standard deviation of the boundary points
    >>> bds, bds_err = nc.get_iboundaries(numseg)
    >>> # get the information of all segments
    >>> info_df = nc.get_info(bds)
    >>> # plot the data and the segments
    >>> nc.plot(info_df)

    """

    def __init__(
        self,
        X,
        Y,
        err=None,
        yrange=None,
        prior=None,
        estimate_err="default",
        minlen=3,
        method="simpson",
    ):
        # Load settings
        self.X = np.asarray(X)
        self.Y = np.asarray(Y)
        self.method = method
        if isinstance(err, (list, np.ndarray)):
            self.err = np.asarray(err)
        else:
            self.err = None
        self.start = 0
        self.end = self.X.shape[0]
        if minlen >= 3:
            self.minlen = minlen
        else:
            warning("Nunchaku: minlen must be >= 3. Reset to 3.")
            self.minlen = 3
        # handle estimate_err
        if estimate_err == "default":
            # if Y has 3 replicates and err is none
            if (self.Y.ndim > 1) and (self.Y.shape[0] >= 3) and (self.err is None):
                estimate_err = True
            else:
                estimate_err = False
        # if err is provided, do not estimate_err (overwrite user's setting)
        if self.err is not None:
            estimate_err = False
        # if err is not provided but Y is 1-D, impossible to estimate_err
        elif self.Y.ndim == 1:
            estimate_err = False
        # if err is provided but Y is 2-D, throw error
        if self.err is not None and self.Y.ndim > 1:
            raise ValueError("When err is provided, Y should be 1-D.")
        # now estimate err
        self.estimate_err = estimate_err
        if estimate_err:
            # x, y, instead of X, Y, are what the methods actually use
            self.x = self.X
            self.y = self.Y.mean(axis=0)
            # OK to write err because estimate_err is True only when err is None
            self.err = self.Y.std(axis=0)
        else:
            self.x = self.X
            self.y = self.Y
            if self.Y.ndim == 1:
                self.nreplicates = 1
            else:
                self.nreplicates = self.Y.shape[0]
        # handle estimated err=0 when replicates have the same value by chance
        if self.err is not None:
            self.err[self.err == 0] = self.err[self.err > 0].mean()
        # prior
        if prior:
            if len(prior) == 2:
                prior.append(min(-self.x[-1] * prior[1], self.x[0] * prior[0]))
                prior.append(max(-self.x[-1] * prior[0], self.x[0] * prior[1]))
            elif len(prior) != 4:
                raise ValueError(f"len(prior) should be 2 or 4, not {prior}.")
            self.prior = prior
        else:
            if yrange:
                m_max = (yrange[1] - yrange[0]) / np.min(np.diff(self.x))
            else:
                warning(
                    """Nunchaku: neither the prior of gradient and intercept nor the range of y is given.
                Using the min and max of y as the range of y to estimate of prior.
                """
                )
                m_max = (np.max(self.y) - np.min(self.y)) / np.min(np.diff(self.x))
            c_max = max(m_max * self.x[-1], m_max * self.x[0])
            prior = [-m_max, m_max, -c_max, c_max]
            self.prior = prior
        self.logpmc = -np.log((prior[1] - prior[0]) * (prior[3] - prior[2]))
        # results
        if self.err is not None:
            self.evidence = self._cal_evidence()
        else:
            self.U, self.D, self.L = self._cal_evidence()
            if self.nreplicates > 1:
                self.sigma0 = self.Y.std(axis=0).mean()
            else:
                self.sigma0 = 1
        self.logZ = dict()
        self.sigma_mle = dict()
        self.large = False

    def _cal_evidence(self):
        """Calculate evidence for each possible segment between start and end."""
        X, Y, err, start, end, minlen = (
            self.x,
            self.y,
            self.err,
            self.start,
            self.end,
            self.minlen,
        )
        # Matrix to record results
        # calculate evidence
        if self.err is None:
            results_U = np.ones((len(X), len(X)), dtype=np.longdouble) * np.nan
            results_D = np.ones((len(X), len(X)), dtype=np.longdouble) * np.nan
            results_L = np.ones((len(X), len(X)), dtype=np.longdouble) * np.nan
            U, D = mc_t()
            for st in tqdm(
                range(start, end - minlen + 1), desc="getting evidence matrix"
            ):
                for ed in range(st + minlen, end + 1):  # confirm?
                    # Run calculation and update init_guess
                    evi_u = self._cal_evidence_unknown_err(st, ed, U)
                    results_U[st, ed - 1] = evi_u
                    evi_d = self._cal_evidence_unknown_err(st, ed, D)
                    results_D[st, ed - 1] = evi_d
                    results_L[st, ed - 1] = (ed - st) * self.nreplicates
            return results_U, results_D, results_L
        else:
            results = np.ones((len(X), len(X))) * np.nan
            logL = mc()
            for st in range(start, end - minlen + 1):
                for ed in range(st + minlen, end + 1):  # confirm?
                    evi = logL(X[st:ed], Y[st:ed], err[st:ed], ed - st)
                    # unknown bug in either builtin sum or numpy sum
                    if evi > 9e8:
                        evi = -np.inf
                    results[st, ed - 1] = evi  # must be (end - 1)?
            return results

    def get_number(self, max_num):
        """Get the number of linear segments with the highest evidence.

        Parameters
        ----------
        max_num : list of int
            maximum number of linear segments

        Returns
        -------
        best_numseg : int
            the number of linear segments with the highest evidence.
        evi : float
            log10 of the evidence of each number of linear segments.

        Raises
        ------
        OverflowError
            when numerical integration yields infinity.

        """
        evi = []
        if self.err is not None:
            res = self.evidence.copy()
            res = res.astype(np.longdouble)
            # normalise to avoid overflow
            log_norm_factor = np.nanmax(res)
            res = np.exp(res - np.nanmax(res))
            res[np.isnan(res)] = 0
            for M in range(1, max_num + 1):
                with np.errstate(divide="ignore", invalid="ignore"):
                    evi_M = (
                        np.log(self._findZ(res, M))
                        + self._mc_logprior(M)
                        + self.logpmc * M
                        + log_norm_factor * M
                    ) / np.log(10)
                evi.append(evi_M)
        else:
            for M in tqdm(range(1, max_num + 1), desc="getting model evidence"):
                with np.errstate(divide="ignore", invalid="ignore"):
                    if M > 3:
                        logZ = self._findZ_unknown_err_numerical(M, method=self.method)
                        self.logZ[M] = logZ  # store Z for finding iboundaries
                        log_evi = logZ + (
                            -len(self.x) * self.nreplicates / 2 + M
                        ) * np.log(2 * np.pi)
                    else:  # use analytical sum where possible
                        logZ = self._findZ_unknown_err_analytical(M)
                        self.logZ[M] = logZ
                        log_evi = (
                            logZ
                            + loggamma((len(self.x) * self.nreplicates - 1) / 2 - M)
                            + (-len(self.x) * self.nreplicates / 2 + M)
                            * np.log(2 * np.pi)
                        )
                    evi_M = (
                        +log_evi + self._mc_logprior(M) + self.logpmc * M
                    ) / np.log(10)
                evi.append(evi_M)
            # check
            if len(evi) > 3:
                if not (np.any(np.isfinite(np.array(evi[3:])))):
                    warning(f"Nunchaku: the evidence may be numerically too small.")
            elif not np.any(np.isfinite(np.array(evi))):
                warning(f"Nunchaku: the evidence may be numerically too small.")
        ind = np.nanargmax(evi)
        best_numseg = ind + 1
        # check
        if best_numseg == max_num:
            warning(
                "Nunchaku: the best number of segments equals the largest candidate."
            )
        return best_numseg, evi

    def get_info(self, boundaries):
        """Return a Pandas dataframe that describes the segments within given internal boundaries,
        i.e. excluding the first (0) and last (`len(x)`) indices of the data.

        Parameters
        ----------
        boundaries : list of int
            a list of indices of boundary points

        Returns
        -------
        df : pd.Dataframe
            Pandas dataframe that describes the segments within given internal boundaries,

        """
        # quick check to make sure boundaries are sensible
        x, y = (self.x, self.y)
        keys = [
            "start",
            "end",
            "gradient",
            "intercept",
            "rsquare",
            "x range",
            "y range",
            "delta x",
            "delta y",
        ]
        d = {k: [] for k in keys}
        d["start"] = [0] + list(map(lambda x: x + 1, boundaries))
        d["end"] = boundaries + [len(self.x) - 1]
        for st, ed in zip(d["start"], d["end"]):
            if y.ndim > 1:
                # flatten for regression
                x_flat = np.append([], [x[st : ed + 1]] * y.shape[0])
                y_flat = y[:, st : ed + 1].flatten(order="C")
                y_mn = y[:, st : ed + 1].mean(axis=0)
            else:
                x_flat = x[st : ed + 1]
                y_flat = y[st : ed + 1]
                y_mn = y[st : ed + 1]
            d["x range"].append((x_flat[0], x_flat[-1]))
            d["y range"].append((y_mn[0], y_mn[-1]))
            d["delta x"].append(x_flat[-1] - x_flat[0])
            d["delta y"].append(y_mn[-1] - y_mn[0])
            lin_res = linregress(x_flat, y_flat)
            d["gradient"].append(lin_res.slope)
            d["intercept"].append(lin_res.intercept)
            d["rsquare"].append(lin_res.rvalue**2)
        return pd.DataFrame(d)

    def get_iboundaries(self, numseg, round=True, bd_err=True):
        """Return the mean and standard deviation of the internal boundary indices,
        i.e. excluding the first (0) and last (`len(x)`) indices of the data.

        Parameters
        ----------
        numseg : int
            number of linear segments
        round : bool, default True
            whether to round the returned mean to integer
        bd_err : bool, default True
            whether to estimate the error of the boundary positions. If False,
            it takes shorter to get the internal boundaries.

        Returns
        -------
        boundaries : list of int or float
            Indices of internal boundaries
        boundaries_err : list of float
            Error of the indices of internal boundaries

        Raises
        ------
        OverflowError
            when numerical integration yields infinity.

        """
        boundaries = []
        boundaries_err = []
        if self.err is not None:
            res = self.evidence.copy()
            res = res.astype(np.longdouble)
            # normalise to avod overflow
            # log_norm_factor = np.nanmax(res)
            res = np.exp(res - np.nanmax(res))
            res[np.isnan(res)] = 0
            Z = self._findZ(res, numseg)
            for j in range(1, numseg):
                coo = self._find_moment(res, numseg, j) / Z
                boundaries.append(coo)
                coo2 = self._find_moment(res, numseg, j, moment=2) / Z
                boundaries_err.append(np.sqrt(coo2 - coo**2))
        else:
            if numseg > 3:
                for j in tqdm(
                    range(1, numseg),
                    desc="getting internal boundaries",
                ):
                    coo = np.exp(
                        self._find_moment_unknown_err_numerical(numseg, j, method=self.method)
                        - self.logZ[numseg],
                        dtype=np.longdouble,
                    )
                    # quick check
                    if coo >= self.minlen and coo < len(self.x):
                        pass
                    else:
                        warning(
                            "Nunchaku: numerical integration is probably inaccurate."
                        )
                    boundaries.append(coo)
                    if bd_err:
                        coo2 = np.exp(
                            self._find_moment_unknown_err_numerical(numseg, j, moment=2, method=self.method)
                            - self.logZ[numseg],
                            dtype=np.longdouble,
                        )
                        boundaries_err.append(np.sqrt(coo2 - coo**2))
            else:
                for j in tqdm(
                    range(1, numseg),
                    desc="getting internal boundaries",
                ):
                    coo = np.exp(
                        self._find_moment_unknown_err_analytical(numseg, j)
                        - self.logZ[numseg],
                        dtype=np.longdouble,
                    )
                    boundaries.append(coo)
                    if bd_err:
                        coo2 = np.exp(
                            self._find_moment_unknown_err_analytical(
                                numseg, j, moment=2
                            )
                            - self.logZ[numseg],
                            dtype=np.longdouble,
                        )
                        boundaries_err.append(np.sqrt(coo2 - coo**2))

        if round:
            return list(np.array(boundaries).astype(int)), boundaries_err
        else:
            return boundaries, boundaries_err

    def plot(
        self,
        info_df=None,
        show=False,
        figsize=(6, 5),
        err_width=1,
        s=10,
        color="red",
        alpha=0.5,
        hlmax={"rsquare": ("orange", "s")},
        hlmin=None,
        **kwargs,
    ):
        """Plot the raw data and the boundary points.

        Parameters
        ----------
        info_df : pandas dataframe, default None
            the pandas dataframe returned by `get_info()`; if None, only the data is shown.
        show : bool, default False
            if True, call `plt.show()`
        figsize : tuple, default (6, 5)
            size of figure passed to `plt.subplots()`
        err_width : float, default 1
            the width of the error bar is this parameter times err times 2 (both
            sides)
        s : float, default 10
            size of the boundary points as passed into `plt.scatter()`
        color : str, default "red"
            color of the boundary points as passed into `plt.scatter()`
        alpha : float, default 0.5
            transparency of the boundary points as passed into `plt.scatter()`
        hlmax : dict, default {"rsquare": ("orange", "s")}
            highlighting the segment with max quantity (e.g. rsquare).
            The key is the column name in `info_df` and the value is a tuple: (color, marker).
        hlmin : dict, optional
            highlighting the segment with min quantity (e.g. rsquare).
            The key is the column name in `info_df` and the value is a tuple: (color, marker).
        **kwargs : keyword arguments
            as passed into `plt.plot()`

        Returns
        -------
        fig : `matplotlib.figure.Figure` object
            Matplotlib Figure object
        axes : `matplotlib.axes.Axes` object
            Matplotlib Axes object

        """

        if self.y.ndim > 1:
            y = self.y.mean(axis=0)
            err = None
        else:
            y = self.y
            err = self.err
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(self.x, y, color="blue")
        if err is not None:
            ax.fill_between(
                self.x,
                y - err_width * err,
                y + err_width * err,
                alpha=0.1,
                color="blue",
            )

        if info_df is not None:
            # handle how to highlight segments
            if hlmax is not None:
                idx_ignore_max = [info_df[k].idxmax() for k in hlmax.keys()]
                idx_color_max = [v[0] for v in hlmax.values()]
                idx_marker_max = [v[1] for v in hlmax.values()]
            else:
                idx_ignore_max = []
                idx_color_max = []
                idx_marker_max = []

            if hlmin is not None:
                idx_ignore_min = [info_df[k].idxmin() for k in hlmin.keys()]
                idx_color_min = [v[0] for v in hlmin.values()]
                idx_marker_min = [v[1] for v in hlmin.values()]
            else:
                idx_ignore_min = []
                idx_color_min = []
                idx_marker_min = []

            idx_ignore = idx_ignore_max + idx_ignore_min
            idx_color = idx_color_max + idx_color_min
            idx_marker = idx_marker_max + idx_marker_min

            for j in range(info_df.shape[0]):
                if j not in idx_ignore:
                    bd_start = info_df.loc[j, "start"]
                    bd_end = info_df.loc[j, "end"]
                    slope = info_df.loc[j, "gradient"]
                    intercept = info_df.loc[j, "intercept"]
                    y_start = slope * self.x[bd_start] + intercept
                    y_end = slope * self.x[bd_end] + intercept
                    ax.plot(
                        [self.x[bd_start], self.x[bd_end]],
                        [y_start, y_end],
                        color=color,
                        alpha=alpha,
                        marker="o",
                        markersize=s,
                        **kwargs,
                    )
        for idx, cl, mk in zip(idx_ignore, idx_color, idx_marker):
            bd_start = info_df.loc[idx, "start"]
            bd_end = info_df.loc[idx, "end"]
            slope = info_df.loc[idx, "gradient"]
            intercept = info_df.loc[idx, "intercept"]
            y_start = slope * self.x[bd_start] + intercept
            y_end = slope * self.x[bd_end] + intercept
            ax.plot(
                [self.x[bd_start], self.x[bd_end]],
                [y_start, y_end],
                color=cl,
                alpha=alpha,
                marker=mk,
                markersize=s,
                **kwargs,
            )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        if show:
            plt.show()
        return fig, ax

    def plot_matrix(self, show=False, figsize=(6, 5), **kwargs):
        """Plot the evidence for all calcuated segments.

        Parameters
        ----------
        show : bool
            if True, call `plt.show()`

        figsize : tuple, default (6, 5)
            figsize passed on to `matplotlib.pyplot.figure`.

        kwargs :
            keyword arguments to be passed to `matplotlib.axes.Axes.plot`
            when result="from", otherwise `matplotlib.axes.Axes.imshow`.

        Returns
        -------
        fig : `matplotlib.figure.Figure` object
            Matplotlib Figure object
        axes : `matplotlib.axes.Axes` object
            Matplotlib Axes object

        Raises
        ------
        NotImplementedError
            when the error is neither estimated nor provided.

        Examples
        --------
        `plot_matrix()` returns both the figure and axes, enabling users to customise them

        >>> from nunchaku.nunchaku import nunchaku
        >>> nc = nunchaku(x, y)
        >>> fig, ax = nc.plot_matrix()
        >>> ax.set_ylim(200,)

        """
        if self.err is not None:
            res = self.evidence
        else:
            raise NotImplementedError(
                "This method is only available if error is estimated or provided."
            )
        fig = plt.figure(constrained_layout=True, figsize=figsize)
        # create three axes
        gs = fig.add_gridspec(
            2,
            2,
            width_ratios=(4, 1),
            height_ratios=(1, 4),
        )
        ax = fig.add_subplot(gs[1, 0])
        ax_mgx = fig.add_subplot(gs[0, 0], sharex=ax)
        ax_mgy = fig.add_subplot(gs[1, 1], sharey=ax)
        # calculate marginal
        res_norm = np.exp(res - np.nanmax(res))
        with np.errstate(invalid="ignore"):  # ignore the zero division case
            mgx = np.nansum(res_norm, axis=0) / np.sum(~np.isnan(res_norm), axis=0)
            mgy = np.nansum(res_norm, axis=1) / np.sum(~np.isnan(res_norm), axis=1)
        img = ax.imshow(res, origin="lower", aspect="auto", **kwargs)
        fig.colorbar(img, ax=ax, location="left", use_gridspec=True)
        ax.set_ylabel("index of start")
        ax.set_xlabel("index of end")
        ax_mgx.plot(mgx)
        ax_mgx.xaxis.set_tick_params(labelbottom=False)
        ax_mgy.plot(mgy, range(len(mgy)))
        ax_mgy.yaxis.set_tick_params(labelleft=False)
        axes = [ax, ax_mgx, ax_mgy]
        if show:
            plt.show()
        return fig, axes

    ### Internal functions

    def _cal_evidence_unknown_err(self, start, end, func):
        """calculate evidence without err

        Parameters
        ----------
        start : init
            start of segment
        end : int
            end of segment (exclusive)

        """
        X, Y = (self.x, self.y)
        # flatten multiple reps
        if Y.ndim > 1:
            X_flat = np.append([], [X[start:end]] * Y.shape[0])  # flatten X
            Y_flat = Y[:, start:end].flatten(order="C")
            n_flat = len(X[start:end]) * Y.shape[0]
        else:
            X_flat = X[start:end]
            Y_flat = Y[start:end]
            n_flat = len(X[start:end])
        return func(X_flat, Y_flat, n_flat)

    def _mc_logprior(self, numseg):
        """return the log value of the uniform prior given number of boundary points"""
        if self.err is not None:
            res = self.evidence.copy()
        else:
            res = self.D.copy()
        res[~np.isnan(res)] = 1
        res[np.isnan(res)] = 0
        return -np.log(self._findZ(res, numseg))

    def _findZ(self, exp_res, number, vec=None):
        """finding the normalising factor of the posterior"""
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                return exp_res[0, -1]
            else:
                f_M = list(exp_res[:, datalen - 1])
                f_M = np.array([f_M[1:] + [0]])
                return self._findZ(exp_res, number - 1, f_M)
        else:
            if number == 1:
                return np.matmul(exp_res[0, :], vec.T)[0]
            else:
                f_M = []
                for n in range(datalen):
                    f_M.append(np.matmul(exp_res[n, :], vec.T)[0])
                f_M = np.array([f_M[1:] + [0]])
                return self._findZ(exp_res, number - 1, f_M)

    def _find_moment(self, exp_res, number, k, moment=1, vec=None):
        """finding the moments of the posterior"""
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                return None
            else:  # k < number when vec is None
                f_M = list(exp_res[:, datalen - 1])
                f_M = np.array([f_M[1:] + [0]])
                return self._find_moment(exp_res, number - 1, k, moment, f_M)
        else:
            if number == 1:
                if k == number:
                    return np.matmul(
                        exp_res[0, :],
                        vec.T * np.arange(datalen).reshape(datalen, 1) ** moment,
                    )[0]
                else:
                    return np.matmul(exp_res[0, :], vec.T)[0]
            else:
                f_M = []
                if k == number:
                    for n in range(datalen):
                        f_M.append(
                            np.matmul(
                                exp_res[n, :],
                                vec.T
                                * np.arange(datalen).reshape(datalen, 1) ** moment,
                            )[0]
                        )
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_moment(exp_res, number - 1, k, moment, f_M)
                else:
                    for n in range(datalen):
                        f_M.append(np.matmul(exp_res[n, :], vec.T)[0])
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_moment(exp_res, number - 1, k, moment, f_M)

    def _findZ_unknown_err_analytical(self, number):
        """finding the normalisation factor when sigma is unknown.

        The 2pi term and the gamma term are handled in get_number().
        """
        exp_u = self._matrix_fill(self.U)
        exp_d = self._matrix_fill(self.D)
        N = len(self.x)
        M = number
        minlen = self.minlen
        # upper limits of (number - 1) iboundries
        u_limits = [N - k * minlen for k in range(number - 1, 0, -1)]
        l_limits = minlen - 1
        # list of possible values of each iboundary (end point)
        ib_ranges = [range(l_limits, u) for u in u_limits]
        all_combs = product(*ib_ranges)
        len_all_combs = np.prod(np.array(u_limits) - l_limits)
        # calculate sum
        evi = 0
        # for ibs in tqdm(all_combs, total=len_all_combs):
        for ibs in all_combs:
            # including start and end
            begs_minus_1 = [-1] + list(ibs)
            ends = list(ibs) + [N - 1]
            d_i = np.array(
                [exp_d[b + 1, e] for b, e in zip(begs_minus_1, ends)],
                dtype=np.longdouble,
            )
            D = np.prod(d_i)
            u_i = np.array(
                [exp_u[b + 1, e] for b, e in zip(begs_minus_1, ends)],
                dtype=np.longdouble,
            )
            U = np.sum(u_i)
            # some constants like 2pi and gamma are handled in get_numbers()
            evi += D * U ** (M - (N * self.nreplicates - 1) / 2) / 2
        return np.log(evi, dtype=np.longdouble)

    @staticmethod
    def _matrix_fill(matrix):
        """copy the result matrix and replace nans with zeros."""
        res = matrix.copy()
        res = res.astype(np.longdouble)
        # normalise to avoid overflow
        res[np.isnan(res)] = 0
        return res

    def _exp_res_sigma(self, sigma):
        """
        when sigma is unknown and numerical integration is necessary,
        use this function to generate a matrix as a function of sigma,
        from which we get P(D|segment, sigma) for each possible segment.

        the 2pi term is left out for get_number() to handle.
        """
        return (
            np.exp(
                -(self.U) / sigma**2
                + (2 - self.L) * np.log(sigma, dtype=np.longdouble),
                # + (1 - self.L / 2) * np.log(2 * np.pi, dtype=np.longdouble),
                dtype=np.longdouble,
            )
            * self.D
        )

    def _findZ_sigma(self, sigma, number, exp_res=None, vec=None):
        """finding the normalising factor of the posterior as a function of sigma when sigma is unknown."""
        if exp_res is None:
            exp_res = self._matrix_fill(self._exp_res_sigma(sigma))
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                return exp_res[0, -1]
            else:
                f_M = list(exp_res[:, datalen - 1])
                f_M = np.array([f_M[1:] + [0]])
                return self._findZ_sigma(sigma, number - 1, exp_res, f_M)
        else:
            if number == 1:
                return np.matmul(exp_res[0, :], vec.T)[0]
            else:
                f_M = []
                for n in range(datalen):
                    f_M.append(np.matmul(exp_res[n, :], vec.T)[0])
                f_M = np.array([f_M[1:] + [0]])
                return self._findZ_sigma(sigma, number - 1, exp_res, f_M)

    def _find_moment_sigma(self, sigma, number, k, moment=1, exp_res=None, vec=None):
        """finding the moments of the posterior as a function of sigma when sigma is unknown."""
        if exp_res is None:
            exp_res = self._matrix_fill(self._exp_res_sigma(sigma))
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                return None
            else:  # k < number when vec is None
                f_M = list(exp_res[:, datalen - 1])
                f_M = np.array([f_M[1:] + [0]])
                return self._find_moment_sigma(
                    sigma, number - 1, k, moment, exp_res, f_M
                )
        else:
            if number == 1:
                if k == number:
                    return np.matmul(
                        exp_res[0, :],
                        vec.T * np.arange(datalen).reshape(datalen, 1) ** moment,
                    )[0]
                else:
                    return np.matmul(exp_res[0, :], vec.T)[0]
            else:
                f_M = []
                if k == number:
                    for n in range(datalen):
                        f_M.append(
                            np.matmul(
                                exp_res[n, :],
                                vec.T
                                * np.arange(datalen).reshape(datalen, 1) ** moment,
                            )[0]
                        )
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_moment_sigma(
                        sigma, number - 1, k, moment, exp_res, f_M
                    )
                else:
                    for n in range(datalen):
                        f_M.append(np.matmul(exp_res[n, :], vec.T)[0])
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_moment_sigma(
                        sigma, number - 1, k, moment, exp_res, f_M
                    )

    def _find_moment_unknown_err_analytical(self, number, k, moment=1):
        """finding the moments analytically when sigma is unknown.

        the 2pi term and the gamma term are ignored:
        that's ok because the Z have the same terms ignored.
        """
        exp_u = self._matrix_fill(self.U)
        exp_d = self._matrix_fill(self.D)
        N = len(self.x)
        M = number
        minlen = self.minlen
        # upper limits of (number - 1) iboundries
        u_limits = [N - j * minlen for j in range(number - 1, 0, -1)]
        l_limits = minlen - 1
        # list of possible values of each iboundary (end point)
        ib_ranges = [range(l_limits, u) for u in u_limits]
        all_combs = product(*ib_ranges)
        # calculate sum
        evi = 0
        # for ibs in tqdm(all_combs, total=len_all_combs):
        for ibs in all_combs:
            # including start and end
            begs_minus_1 = [-1] + list(ibs)
            ends = list(ibs) + [N - 1]
            d_i = np.array(
                [exp_d[b + 1, e] for b, e in zip(begs_minus_1, ends)],
                dtype=np.longdouble,
            )
            D = np.prod(d_i)
            u_i = np.array(
                [exp_u[b + 1, e] for b, e in zip(begs_minus_1, ends)],
                dtype=np.longdouble,
            )
            U = np.sum(u_i)
            evi += (
                D
                * U ** (M - (N * self.nreplicates - 1) / 2)
                / 2
                # * gamma((N - 1) / 2 - M)
                * ibs[k - 1] ** moment
            )
        return np.log(evi, dtype=np.longdouble)

    def _findZ_unknown_err_numerical(self, number, method="simpson"):
        """finding the normalisation factor numerically when sigma is unknown."""
        sigma_mle = self._find_sigma_by_EM(number)
        # store sigma_mle for finding iboundaries
        self.sigma_mle[number] = sigma_mle
        if np.isfinite(sigma_mle):
            norm = self._findZ_sigma(sigma_mle, number)
        else:
            norm = 1
        if np.isfinite(norm):
            integrand = lambda sigma, M: self._findZ_sigma(sigma, M) / norm
        else:
            raise OverflowError("Integrand is too large when finding model evidence.")
        if method == "quad" or np.isnan(sigma_mle):
            # if MLE of sigma is nan, fall back to quad
            res = quad(
                integrand,
                0,
                np.inf,
                args=(number,),
                epsabs=0.0,
                epsrel=1e-10,
            )
        elif method == "simpson":
            low = sigma_mle / 10
            high = sigma_mle * 10
            x1 = np.logspace(np.log10(low), np.log10(sigma_mle), 100)
            x2 = np.logspace(np.log10(sigma_mle), np.log10(high), 100)
            itg_vec = np.vectorize(integrand)
            y1 = itg_vec(x1, number)
            y2 = itg_vec(x2, number)
            res = simpson(y1, x1) + simpson(y2, x2)
            res = (res, 0.0)
        if np.isfinite(res[0]):
            if res[0] <= res[1]:
                warning(
                    "Nunchaku: Integral may not be accurate when finding model evidence."
                )
            return np.log(res[0]) + np.log(norm)
        else:
            raise OverflowError("Integral is too large when finding model evidence.")

    def _find_moment_unknown_err_numerical(self, number, k, moment=1, method="simpson"):
        """finding the moments numerically when sigma is unknown."""
        sigma_mle = self.sigma_mle[number]
        if np.isfinite(sigma_mle):
            norm = self._find_moment_sigma(sigma_mle, number, k, moment)
        else:
            norm = 1
        if np.isfinite(norm):
            integrand = (
                lambda sigma, M, k, mom: self._find_moment_sigma(sigma, M, k, mom)
                / norm
            )
        else:
            raise OverflowError("Integrand is too large when finding moment.")
        if method == "quad" or np.isnan(sigma_mle):
            # if MLE of sigma is nan, fall back to quad
            res = quad(
                integrand,
                0,
                np.inf,
                args=(number, k, moment),
                epsabs=0.0,
                epsrel=1e-10,
            )
        elif method == "simpson":
            low = sigma_mle / 10
            high = sigma_mle * 10
            x1 = np.logspace(np.log10(low), np.log10(sigma_mle), 100)
            x2 = np.logspace(np.log10(sigma_mle), np.log10(high), 100)
            itg_vec = np.vectorize(integrand)
            y1 = itg_vec(x1, number, k, moment)
            y2 = itg_vec(x2, number, k, moment)
            res = simpson(y1, x1) + simpson(y2, x2)
            res = (res, 0.0)
        if np.isfinite(res[0]):
            if res[0] <= res[1]:
                warning("Nunchaku: Integral may not be accurate when finding moment.")
            return np.log(res[0]) + np.log(norm)
        else:
            raise OverflowError("Integral is too large when finding moment.")

    def _find_expectation_sigma_by_segment(
        self, sigma, number, k, exp_res=None, vec=None
    ):
        """helper function to get the MLE of sigma by expectation-maximisation."""
        if exp_res is None:
            exp_res = self._matrix_fill(self._exp_res_sigma(sigma))
        Umat = self._matrix_fill(self.U)
        datalen = len(self.x)
        if vec is None:
            if number == 1:
                # then k must be 1.
                return exp_res[0, -1] * Umat[0, -1]
            else:
                if k == number:  # the last segment
                    f_M = list(exp_res[:, datalen - 1] * Umat[:, datalen - 1])
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_expectation_sigma_by_segment(
                        sigma, number - 1, k, exp_res, f_M
                    )
                else:
                    f_M = list(exp_res[:, datalen - 1])
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_expectation_sigma_by_segment(
                        sigma, number - 1, k, exp_res, f_M
                    )
        else:
            if number == 1:
                if k == 1:  # the first segment
                    return np.matmul(exp_res[0, :] * Umat[0, :], vec.T)[0]
                else:
                    return np.matmul(exp_res[0, :], vec.T)[0]
            else:
                f_M = []
                if k == number:
                    for n in range(datalen):
                        f_M.append(np.matmul(exp_res[n, :] * Umat[n, :], vec.T)[0])
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_expectation_sigma_by_segment(
                        sigma, number - 1, k, exp_res, f_M
                    )
                else:
                    for n in range(datalen):
                        f_M.append(np.matmul(exp_res[n, :], vec.T)[0])
                    f_M = np.array([f_M[1:] + [0]])
                    return self._find_expectation_sigma_by_segment(
                        sigma, number - 1, k, exp_res, f_M
                    )

    def _find_expectation_sigma(self, sigma0, number):
        """helper function to get the MLE of sigma by expectation-maximisation."""
        E = 0
        for k in range(1, number + 1):
            E += self._find_expectation_sigma_by_segment(sigma0, number, k)
        # Z given sigma0
        Z = self._findZ_sigma(sigma=sigma0, number=number)
        N = len(self.x) * self.nreplicates
        return np.sqrt(E / Z / (N / 2 - number))

    def _find_sigma_by_EM(self, number, reltol=1e-5, max_attempt=100):
        """Get the MLE of sigma by expectation-maximisation."""
        sigma0 = self.sigma0
        for j in range(max_attempt):
            sigma = self._find_expectation_sigma(sigma0, number)
            if np.isnan(sigma):
                warning(
                    f"Nunchaku: failed to estiamte MLE of sigma when the number of segment is {number}."
                )
                return np.nan
            reldiff = np.abs(sigma - sigma0) / sigma0
            if reldiff < reltol:
                # for some reason sigma is float128 if not converted
                return float(sigma)
            else:
                sigma0 = sigma
        else:
            warning(
                f"""Nunchaku: EM algorithm does not yet converge after {max_attempt} attempts.
                Current relative difference: {reldiff}."""
            )
            return float(sigma)

    def get_MLE_of_error(self, numseg):
        """Returns the MLE of the data's error estimated by expectation-maximisation.

        Parameters
        ----------
        numseg : int
            number of linear segments

        Returns
        -------
        err : float
            The MLE of the data's error, assuming homogeneity of variance.

        Raises
        ------
        NotImplementedError
            when the error is already provided or estimated.

        """
        if self.err is not None:
            raise NotImplementedError(
                "MLE of error is only available when error is neither provided nor estimated."
            )
        else:
            return self._find_sigma_by_EM(numseg)


def get_example_data(plot=False):
    """Return example data, with x being cell number and y being three replicates of OD measurement.

    Parameters
    ----------
    plot : bool, default False
        If true, plot the example data.

    Returns
    -------
    x : 1D numpy array
        Example data of x
    y : 2D numpy array
        Example data of y

    Examples
    --------
    >>> from nunchaku.nunchaku import get_example_data
    >>> x, y = get_example_data()
    """
    x, y = return_data()
    if plot:
        fig, ax = plt.subplots()
        for j in range(y.shape[0]):
            ax.scatter(x, y[j, :], alpha=0.7, color="b")
        ax.set_xlabel("cell number")
        ax.set_ylabel("optical density (OD)")
        plt.show()
    return x, y
