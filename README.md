### 3.0 What the dynamic model is doing (math view)

We treat the process as a discrete-time mapping

$$y(t) = f\big( u(t), u(t-1), \dots, u(t-k_u),\; y(t-1), \dots, y(t-k_y) \big)$$

where:
- $u(t) = [U_1(t), U_2(t)]$ are the inputs at time $t$
- $y(t) = [Y_1(t), Y_2(t)]$ are the outputs at time $t$
- $k_u =$ `input_lags`, $k_y =$ `output_lags`

In the dynamic cells we build, for each valid time index $t$:
- a **feature vector** $x(t)$ that stacks all chosen lags of $u$ and $y$
- a **target** $y(t)$ (the outputs at the current time)

Random Forest and XGBoost then learn an approximation $\hat f$ so that

$$\hat y(t) = \hat f\big( u(t), \dots, u(t-k_u),\; y(t-1), \dots, y(t-k_y) \big) \approx y(t).$$

If the model is good and the lags are sufficient, the **dynamic test plots** will show the predicted trajectories $\hat Y_1, \hat Y_2$ closely tracking the true $Y_1, Y_2$ even when the inputs move through new regimes (good generalization to unseen input sequences).