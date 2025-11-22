# content.py

content_data2 = {
    "1. Introduction": [
        "Ho & Lee introduced some time dependence into the coefficient of their random walk. This allows the yield curve to be fitted.",
        r"\[ dr = \theta(t)dt+ \sigma^{1/2}dW \]"
    ],

    "2. Model Setup": [
        "Consider the short rate model under the risk-neutral measure:",
        r"\[ dr_t = \theta(t) dt + \sigma dW_t \]",
        "Here, θ(t) is chosen so that the model fits the initial term structure."
    ],

    "3. Solution": [
        "The analytical solution for the short rate process is:",
        r"\[ r_t = r_0 e^{-a t} + \int_0^t e^{-a (t-s)} \theta(s) ds + \sigma \int_0^t e^{-a (t-s)} dW_s \]"
    ]
}



content_data = {
    "1. Introduction": [
        "Ho & Lee introduced some time dependence into the coefficient of their random walk. This allows the yield curve to be fitted.",
        r"\[ dr = \theta(t) dt + \sigma^{1/2} dW \]",
        "The value of zero-coupon bonds is again given by",
        r"\[ V = e^{A(t) - rB(t)} \]"
    ],

    "2. Bond Pricing Equation (BPE) Setup": [
        "The BPE becomes",
        r"\[ \dot{B}(t) = -1 \]",
        r"\[ \dot{A}(t) = -\frac{1}{2} \sigma B^2 + \theta(t) B(t) \]",
        "which we integrate over \(t\) and \(T\):",
        r"\[ \int_T^t dB = - \int_T^t ds \quad \Rightarrow \quad B(T) = 0 \]",
        r"\[ -B(t) = -(T - t) \]",
        "so",
        r"\[ B(t) = (T - t) \]",
        "and for \(A(t)\):",
        r"\[ \int_T^t dA(s) = -\frac{1}{2} \sigma \int_T^t B^2 ds + \int_T^t \theta(s) B(s) ds \]",
        r"\[ A(T) - A(t) = -\frac{1}{2} \sigma \int_t^T (T - s)^2 ds + \int_T^t \theta(s) (T - s) ds \]",
        r"\[ - A(t) = -\frac{1}{6} \sigma (T - s)^3 + \int_t^T \theta(s) (T - s) ds \]",
        r"\[ A(t) = - \int_t^T \theta(s) (T - s) ds + \frac{1}{6} \sigma (T - t)^3 \]"
    ],

    "3. No-Arbitrage Interpretation": [
        "This model was the first ``no-arbitrage model'' of the term structure of interest rates.",
        "By this is meant that the careful choice of the function \\(\\theta(t)\\) will result in theoretical zero-coupon bond prices, output by the model, which are the same as market prices. (Note that the variables are \\(r\\) and \\(t\\), but we are also explicitly referring to the parameter \\(T\\), the bond maturity.)"
    ],

    "4. Calibration Problem": [
        "The normal way of progressing is that knowing \\(\\theta(t)\\) gives \\(A(t;T)\\); hence we can determine \\(Z(r; t;T)\\):",
        "Working forwards: If we know \\(\\theta(t)\\) then the above gives us the theoretical value of zero-coupon bonds of all maturities. That is, start with model \\((\\theta(t))\\) and find answer \\((Z)\\).",
        "An inverse problem: But what if we know \\(Z\\) from the market, but don’t know the unobservable \\(\\theta\\)? Turn this relationship around and ask the question:",
        "What functional form must we choose for \\(\\theta(t)\\) to make the theoretical value of the discount rates for all maturities equal to the market values?",
        "That is calibration."
    ],

    "5. Calibration Setup": [
        "Suppose we want to calibrate our model today, time \\(t_0\\). Today’s spot interest rate is \\(r_0\\) (which tomorrow will be different) and the discount factors in the market are \\(Z_M(t_0;T)\\). Suppose today is \\(t_0 = \\text{Wednesday 20 May 2008}\\).",
        "Call the special, calibrated, choice for \\(\\theta\\), \\(\\theta_c(t)\\).",
        "We look at the prices of ZCBs on our screens on date \\(t_0\\). Each ZCB has a certain maturity \\(T\\):",
        "To match the market and theoretical bond prices, we must solve",
        r"\[ Z_M(t_0;T) = e^{A(t_0;T) - r_0 (T-t_0)} \]",
        "Taking logarithms of this:",
        r"\[ \log(Z_M(t_0;T)) = A - r_0 B \]",
        "We know the forms of \\(A\\) and \\(B\\):",
        r"\[ \log Z_M = \frac{1}{6} \sigma^2 (T-t_0)^3 - \int_T^{t_0} \theta_c(s) (T-s) ds - r_0 (T-t_0) \]",
        "Rearranging gives:",
        r"\[ \int_T^{t_0} \theta_c(s)(T-s) ds = - \log(Z_M(t_0;T)) - r_0(T-t_0) + \frac{1}{6} \sigma^2 (T-t_0)^3 \]"
    ],

    "6. Solving the Integral Equation": [
        "We know everything on the right-hand side. So this is an \\textit{integral equation} for \\(\\theta_c(t)\\).",
        "It is called an integral equation because the unknown term (which we are solving for) \\(\\theta_c\\) is under the integral sign.",
        "Fortunately it is a simple equation and can be solved by a technique called differentiation under the integral sign. The method is known as Leibniz Rule.",
        "The shortened version of this is:",
        r"\[ \frac{\partial}{\partial x} \int_a^x F(y; x) dy = F(x; x) + \int_a^x \frac{\partial F(y; x)}{\partial x} dy \]",
        "Note that we differentiate with respect to the upper limit.",
        "Observe what happens if we differentiate the integral term with respect to \\(T\\):",
        "Let \\(x \\to T\\), \\(y \\to s\\), \\(F(y; x) \\to (T-s) \\theta_c(s)\\):",
        r"\[ \frac{\partial F}{\partial x} = \frac{\partial F}{\partial T} = \theta_c(s) \]",
        r"\[ F(x; x) = (T-T) \theta_c(T) = 0 \]",
        "First differentiate the LHS once with respect to \\(T\\):",
        r"\[ \frac{d}{dT} \int_T^{t_0} \theta_c(s)(T-s) ds = \int_T^{t_0} \theta_c(s) ds + 0 \]",
        "Differentiate again:",
        r"\[ \frac{d^2}{dT^2} \int_T^{t_0} \theta_c(s)(T-s) ds = \frac{d}{dT} \int_T^{t_0} \theta_c(s) ds = \theta_c(T) \]"
    ],

    "7. Final Calibration Formula": [
        "So, differentiating the RHS twice with respect to \\(T\\) we get:",
        r"\[ \theta_c(T) = - \frac{\partial^2}{\partial t^2} \log(Z_M(t_0;T)) + \sigma^2 (T-t_0) \]",
        "The parameters are not functions of the derivative maturity. Interest rates can depend on time, but cannot have \\(\\sigma(T)\\) in the SDE for the spot rate. That is, we can’t have a short-term interest rate depend on the maturity of a bond. Hence the solution is:",
        r"\[ \theta_c(t) = - \frac{\partial^2}{\partial t^2} \log(Z_M(t_0; t)) + \sigma^2(t-t_0) \]",
        "With this choice for the time-dependent parameter \\(\\theta(t)\\) the theoretical and actual market prices of zero-coupon bonds are the same.",
        "Notes:",
        "1. Now that we know \\(\\theta(t)\\) we can price other fixed income instruments.",
        "2. We say that our prices are consistent with the yield curve.", 
        "3. The same idea can be applied to other spot interest rate models.",    
        "4. This is an inverse problem, and will typically be sensitive to input data (the \\(Z\\))."
    ]
}


