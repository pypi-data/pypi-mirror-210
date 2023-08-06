# Compile with:
# c++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup -I/Library/Frameworks/Python.framework/Headers
# -I"/Users/diego.pedregal/Google Drive/C++/armadillo-10.8.2/include" -llapack -lblas $(python3 -m
# pybind11 --includes) pythonBSM.cpp -o BSMc$(python3-config --extension-suffix)
import numpy as np
from UComp import UCc
from UComp import ETSc


class UCmodel:
    def __init__(self, y: np.array, s: int, u: np.array = np.array([]), model: str = "?/none/?/?",
                 h: int = 9999, lambdaBoxCox: np.array = np.array(1.0), outlier: float = 9999.0, tTest: bool = False,
                 criterion: str = "aic", periods: np.array = np.array([np.nan]), verbose: bool = False,
                 stepwise: bool = False, p0: np.array = np.array([-9999.9]), arma: bool = False,
                 TVP: np.array = np.array([0.0]),
                 trendOptions: str = "none/rw/llt/dt", seasonalOptions: str = "none/equal/different",
                 irregularOptions: str = "none/arma(0,0)"):
        if np.isnan(lambdaBoxCox):
            lambdaBoxCox = np.array([9999.9])
        if (any(np.isnan(TVP)) and u.size != 0):
           TVP = np.zeros(u.shape)
        if (any(np.isnan(TVP))):
            TVP = -9999.99
        if s == 1:
            periods = np.array([1.0]);
        if np.isnan(periods):
            periods = np.array(s / (np.arange(np.floor(s / 2)) + 1))
        # Creating class
        self.y = y
        self.s = s
        self.u = u
        self.model = model
        self.h = h
        self.outlier = -abs(outlier)
        self.tTest = tTest
        self.criterion = criterion
        self.periods = periods
        self.verbose = verbose
        self.stepwise = stepwise
        self.p0 = p0
        self.arma = arma
        self.comp = np.empty((0, 0))
        self.compV = np.empty((0, 0))
        self.p = np.empty((0, 0))
        self.covp = np.empty((0, 0))
        self.grad = np.empty((0, 0))
        self.v = np.empty((0, 0))
        self.yFit = np.empty((0, 0))
        self.yFor = np.empty((0, 0))
        self.yFitV = np.empty((0, 0))
        self.yForV = np.empty((0, 0))
        self.a = np.empty((0, 0))
        self.P = np.empty((0, 0))
        self.eta = np.empty((0, 0))
        self.eps = np.empty((0, 0))
        self.table = ""
        self.iter = 0
        self.criteria = np.empty((0, 0))
        self.lambdaBoxCox = lambdaBoxCox
        self.TVP = TVP
        self.trendOptions = trendOptions
        self.seasonalOptions = seasonalOptions
        self.irregularOptions = irregularOptions

        class hidden:
            d_t: int = 0
            estimOk: str = "Not estimated"
            objFunValue: float = 0.0
            innVariance: float = 1.0
            nonStationaryTerms: int = 0
            ns: np.array = np.array([np.nan])
            nPar: np.array = np.array([np.nan])
            harmonics: np.array = np.array([np.nan])
            rhos = np.ones((len(periods), 1))
            constPar: np.array = np.array([np.nan])
            typePar: np.array = np.array([np.nan])
            cycleLimits: np.array = np.array([np.nan])
            typeOutliers: np.array = np.array([-1, -1])
            truePar: np.array = np.array([np.nan])
            beta: np.array = np.array([np.nan])
            betaV: np.array = np.array([np.nan])
            seas: int = s
            truePar: np.array = np.array([np.nan])
            MSOE = False
            PTSnames = False
        self.hidden = hidden
        # End of class creation

        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        kInitial = rowu

        m1 = UCc.UCfunC("estimate", self.y, u.flatten(), rowu, colu, self.model, self.periods, self.hidden.rhos,
                        self.h, self.tTest, self.criterion, self.hidden.truePar, self.verbose, self.stepwise,
                        self.hidden.estimOk, self.p0, self.v, self.yFitV, self.hidden.nonStationaryTerms,
                        self.hidden.harmonics, self.criteria, self.hidden.beta, self.hidden.betaV, self.hidden.d_t,
                        self.hidden.innVariance, self.hidden.objFunValue,
                        self.outlier, self.arma, self.iter, self.hidden.seas, self.grad, self.hidden.constPar,
                        self.hidden.typePar, self.hidden.ns,
                        self.hidden.nPar, self.hidden.cycleLimits.flatten(), self.hidden.cycleLimits.shape[0], self.hidden.typeOutliers,
                        self.hidden.typeOutliers.shape[0], self.hidden.MSOE, self.hidden.PTSnames, self.lambdaBoxCox, self.TVP,
                        self.trendOptions, self.seasonalOptions, self.irregularOptions)
        if m1.model != "error":  # ERROR!!!
            yFor = np.array(m1.yFor)
            if yFor.size != 0:
                self.yFor = yFor
                self.yForV = np.array(m1.yForV)
#            if (regexp(sys.model, '\?'))
#                sys.model = model;
#            end
            self.model = m1.model
            self.periods = np.array(m1.periods)
            self.hidden.cycleLimits = np.array(m1.cycleLimits)
            if self.hidden.cycleLimits.size > 1:
                self.hidden.cycleLimits = np.reshape(self.hidden.cycleLimits, (np.floor_divide(self.hidden.cycleLimits.size, m1.rowc), m1.rowc))
            self.hidden.rhos = np.array(m1.rhos)
            if self.hidden.rhos.size == 0:
                self.hidden.rhos = np.ones((len(self.periods)))
            self.criteria = np.array(m1.criteria)
            if self.criteria.size == 1:
                self.criteria = np.reshape(self.criteria, (4, 1))
            self.outlier = m1.outlier
            self.hidden.harmonics = np.array(m1.harmonics)
            if self.hidden.harmonics.size == 0:
                self.hidden.harmonics = np.empty((len(self.periods), 1)) * np.nan
            self.hidden.truePar = np.array(m1.p)
            self.p0 = np.array(m1.p0)
            self.grad = np.array(m1.grad)
            self.lambdaBoxCox = m1.lambdaBoxCox
            self.hidden.constPar = np.array(m1.constPar)
            self.hidden.typePar = np.array(m1.typePar)
            self.hidden.d_t = m1.d_t
            self.hidden.innVariance = m1.innVariance
            self.hidden.objFunValue = m1.objFunValue
            self.hidden.beta = np.array(m1.betaAug)
            self.hidden.betaV = np.array(m1.betaAugVar)
            self.h = m1.h
            self.hidden.estimOk = m1.estimOk
            self.hidden.nonStationaryTerms = m1.nonStationaryTerms
            self.hidden.ns = np.array(m1.ns)
            self.hidden.nPar = np.array(m1.nPar)
            self.iter = m1.iter
            if self.outlier != 9999.0 and kInitial > 0:
                nu = len(self.y) + self.h
                k = self.u.size / nu
                nOut = k - kInitial
                if nOut > 0:
                    self.u = np.reshape(self.u, k, nu)
                    self.hidden.typeOutliers = np.reshape(m1.typeOutliers, (np.floor_divide(m1.typeOutliers.size, m1.rowtype), m1.rowtype))


    def components(self):
        u = self.u
        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        m1 = UCc.UCfunC("components", self.y, u.flatten(), rowu, colu, self.model, self.periods, self.hidden.rhos,
                        self.h, self.tTest, self.criterion, self.hidden.truePar, self.verbose, self.stepwise,
                        self.hidden.estimOk, self.p0, self.v, self.yFitV, self.hidden.nonStationaryTerms,
                        self.hidden.harmonics, self.criteria, self.hidden.beta, self.hidden.betaV, self.hidden.d_t,
                        self.hidden.innVariance, self.hidden.objFunValue,
                        self.outlier, self.arma, self.iter, self.hidden.seas, self.grad, self.hidden.constPar,
                        self.hidden.typePar, self.hidden.ns,
                        self.hidden.nPar, self.hidden.cycleLimits.flatten(), self.hidden.cycleLimits.shape[0], self.hidden.typeOutliers,
                        self.hidden.typeOutliers.shape[0], self.hidden.MSOE, self.hidden.PTSnames, self.lambdaBoxCox, self.TVP,
                        self.trendOptions, self.seasonalOptions, self.irregularOptions)
        self.v = np.array(m1.v)
        self.comp = np.array(m1.comp)
        self.compV = np.array(m1.compV)
        self.comp = np.reshape(self.comp, (np.floor_divide(self.comp.size, m1.rowcomp), m1.rowcomp))
        self.compV = np.reshape(self.compV, (np.floor_divide(self.compV.size, m1.rowcomp), m1.rowcomp))
        #m1.compNames = compNames


    def validate(self):
        u = self.u
        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        m1 = UCc.UCfunC("validate", self.y, u.flatten(), rowu, colu, self.model, self.periods, self.hidden.rhos,
                        self.h, self.tTest, self.criterion, self.hidden.truePar, self.verbose, self.stepwise,
                        self.hidden.estimOk, self.p0, self.v, self.yFitV, self.hidden.nonStationaryTerms,
                        self.hidden.harmonics, self.criteria, self.hidden.beta, self.hidden.betaV, self.hidden.d_t,
                        self.hidden.innVariance, self.hidden.objFunValue,
                        self.outlier, self.arma, self.iter, self.hidden.seas, self.grad, self.hidden.constPar,
                        self.hidden.typePar, self.hidden.ns,
                        self.hidden.nPar, self.hidden.cycleLimits.flatten(), self.hidden.cycleLimits.shape[0], self.hidden.typeOutliers,
                        self.hidden.typeOutliers.shape[0], self.hidden.MSOE, self.hidden.PTSnames, self.lambdaBoxCox, self.TVP,
                        self.trendOptions, self.seasonalOptions, self.irregularOptions)
        self.table = ' '.join([str(i) for i in m1.table])
        self.v = np.array(m1.v)
        if self.verbose:
            print(self.table)


    def filter_(self, smooth: str):
        u = self.u
        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        m1 = UCc.UCfunC(smooth, self.y, u.flatten(), rowu, colu, self.model, self.periods, self.hidden.rhos,
                        self.h, self.tTest, self.criterion, self.hidden.truePar, self.verbose, self.stepwise,
                        self.hidden.estimOk, self.p0, self.v, self.yFitV, self.hidden.nonStationaryTerms,
                        self.hidden.harmonics, self.criteria, self.hidden.beta, self.hidden.betaV, self.hidden.d_t,
                        self.hidden.innVariance, self.hidden.objFunValue,
                        self.outlier, self.arma, self.iter, self.hidden.seas, self.grad, self.hidden.constPar,
                        self.hidden.typePar, self.hidden.ns,
                        self.hidden.nPar, self.hidden.cycleLimits.flatten(), self.hidden.cycleLimits.shape[0], self.hidden.typeOutliers,
                        self.hidden.typeOutliers.shape[0], self.hidden.MSOE, self.hidden.PTSnames, self.lambdaBoxCox, self.TVP,
                        self.trendOptions, self.seasonalOptions, self.irregularOptions)
        if (smooth != "disturb"):
            self.a = np.array(m1.a)
            self.P = np.array(m1.P)
            self.v = np.array(m1.v)
            self.F = np.array(m1.F)
            self.yFit = np.array(m1.yFit)
            self.a = np.reshape(self.a, (np.floor_divide(self.a.size, m1.rowa), m1.rowa))
            self.P = np.reshape(self.P, (np.floor_divide(self.a.size, m1.rowa), m1.rowa))
        else:
            self.eps = np.array(m1.eps)
            self.eta = np.array(m1.eta)
            self.eta = np.reshape(self.eta, (np.floor_divide(self.eta.size, m1.roweta), m1.roweta))
        #m1.stateNames = statesN;


    def filter(self):
        self.filter_("filter")


    def smooth(self):
        self.filter_("smooth")


    def disturb(self):
        self.filter_("disturb")


class ETSmodel:
    def __init__(self, y: np.array, s: int, u: np.array = np.array([]), model: str = "???",
                 h: int = 24, criterion: str = "aicc",
                 armaIdent: bool = False, identAll: bool = False, forIntervals: bool = False,
                 bootstrap: bool = False, nSimul: int = 5000, verbose: bool = False,
                 alphaL: np.array = np.array([0, 1]), betaL: np.array = np.array([0, 1]),
                 gammaL: np.array = np.array([0, 1]), phiL: np.array = np.array([0.8, 0.98]),
                 p0: np.array = np.array([-99999]), lambdaBoxCox: np.array = np.array(1.0)):
        self.y = y
        self.u = u
        self.model = model
        self.s = s
        self.h = h
        self.p0 = p0
        self.criterion = criterion
        self.armaIdent = armaIdent
        self.identAll = identAll
        self.forIntervals = forIntervals
        self.bootstrap = bootstrap
        self.nSimul = nSimul
        self.verbose = verbose
        self.alphaL = alphaL
        self.betaL = betaL
        self.gammaL = gammaL
        self.phiL = phiL
        self.yFor = np.empty((0, 0))
        self.yForV = np.empty((0, 0))
        self.comp = np.empty((0, 0))
        self.ySimul = np.empty((0, 0))
        self.table = ""
        self.p = np.empty((0, 0))
        self.lambdaBoxCox = lambdaBoxCox

        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        if np.isnan(lambdaBoxCox):
            lambdaBoxCox = 9999.9
        m1 = ETSc.ETSfunC("estimate", y, u.flatten(), rowu, colu, model, s, h, verbose, criterion,
                          identAll, alphaL, betaL, gammaL, phiL, "standard", forIntervals,
                          bootstrap, nSimul, np.array([0, 0]), armaIdent, p0, lambdaBoxCox)
        if m1.model != "error":  # ERROR!!!
            self.model = m1.model
            self.yFor = np.array(m1.yFor)
            self.yForV = np.array(m1.yForV)
            self.p = np.array(m1.p)
            self.lambdaBoxCox = lambdaBoxCox
            if bootstrap:
                self.ySimul = np.array(m1.ySimul)
                self.ySimul = self.ySimul.reshape((len(self.ySimul) // nSimul, nSimul))


    def components(self):
        u = self.u
        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        m1 = ETSc.ETSfunC("components", self.y, u.flatten(), rowu, colu, self.model, self.s, self.h, False,
                          self.criterion, self.identAll, self.alphaL, self.betaL, self.gammaL, self.phiL,
                          "standard", False, False, 0, np.array([0, 0]), self.armaIdent, self.p0, self.lambdaBoxCox)
        self.compNames = m1.compNames
        nComp = m1.compNames.count('/') + 1
        self.comp = np.array(m1.comp)
        self.comp = np.transpose(self.comp.reshape((nComp, len(self.comp) // nComp)))


    def validate(self):
        u = self.u
        if u.size == 0:
            u = np.array([-99999])
            rowu = 0
            colu = 0
        else:
            if len(u.shape) == 1:
                rowu = 1
                colu = u.shape[0]
            else:
                rowu, colu = u.shape
            if rowu > colu:
                u = np.transpose(u)
                rowu, colu = u.shape
        m1 = ETSc.ETSfunC("validate", self.y, u.flatten(), rowu, colu, self.model, self.s, self.h, False,
                          self.criterion, self.identAll, self.alphaL, self.betaL, self.gammaL, self.phiL,
                          "standard", False, False, 0, np.array([0, 0]), self.armaIdent, self.p0, self.lambdaBoxCox)
        self.compNames = m1.compNames
        nComp = m1.compNames.count('/') + 1
        self.comp = np.array(m1.comp)
        self.comp = np.transpose(self.comp.reshape((nComp, len(self.comp) // nComp)))
        self.table = ' '.join([str(i) for i in m1.table])
        if self.verbose:
            print(self.table)


def UC(y: np.array, s: int, u: np.array = np.array([]), model: str = "?/none/?/?",
       h: int = 9999, lambdaBoxCox: np.array = np.array(1.0), outlier: float = 9999.0, tTest: bool = False,
       criterion: str = "aic", periods: np.array = np.array([np.nan]), verbose: bool = False,
       stepwise: bool = False, p0: np.array = np.array([-9999.9]), arma: bool = False,
       TVP: np.array = np.array([0.0]),
       trendOptions: str = "none/rw/llt/dt", seasonalOptions: str = "none/equal/different",
       irregularOptions: str = "none/arma(0,0)"):
    m = UCmodel(y, s, u, model, h, lambdaBoxCox, outlier, tTest, criterion, periods, verbose, stepwise, p0, arma,
                TVP, trendOptions, seasonalOptions, irregularOptions)
    m.validate()
    m.disturb()
    m.components()
    return m


def ETS(y: np.array, s: int, u: np.array = np.array([]), model: str = "???",
        h: int = 24, criterion: str = "aicc",
        armaIdent: bool = False, identAll: bool = False, forIntervals: bool = False,
        bootstrap: bool = False, nSimul: int = 5000, verbose: bool = False,
        alphaL: np.array = np.array([0, 1]), betaL: np.array = np.array([0, 1]),
        gammaL: np.array = np.array([0, 1]), phiL: np.array = np.array([0.8, 0.98]),
        p0: np.array = np.array([-99999]), lambdaBoxCox: np.array = np.array(1.0)):
    m = ETSmodel(y, s, u, model, h, criterion, armaIdent, identAll, forIntervals,
                 bootstrap, nSimul, verbose, alphaL, betaL, gammaL, phiL, p0, lambdaBoxCox)
    m.validate()
    return m

