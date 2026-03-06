using Turing, Flux, DataFrames, CSV, Plots, Optim
# Load and preprocess data
data = CSV.read("data/org/marketdata/BTCUSDT_15m_2000-11-21 00:00:00_2026-02-23 00:00:00.csv", DataFrame)
features = Matrix(data[:, [:open_price, :high_price, :low_price, :volume,
                           :quote_asset_volume, :number_of_trades,
                           :taker_buy_base_volume, :taker_buy_quote_volume]])
target = data.close_price
μ, σ = mean(features, dims=1), std(features, dims=1)
Lfeatures = (features .- μ) ./ σ

# Create windows
window_size = 5
X, y = [], []
for i in 1:(size(features, 1) - window_size)
    push!(X, features[i:i+window_size-1, :])
    push!(y, target[i+window_size])
end
X = cat(X..., dims=3)
X = permutedims(X, (1, 3, 2))
X = reshape(X, :, size(X)[2])'
y = Float32.(y)

# Define model
n_features = size(features, 2)
input_dim = window_size * n_features

@model function bayesian_nn(x, y; n_hidden=20)
    w1 ~ arraydist([Normal(0, 1) for _ in 1:n_hidden, _ in 1:input_dim])
    b1 ~ arraydist([Normal(0, 1) for _ in 1:n_hidden])
    w2 ~ arraydist([Normal(0, 1) for _ in 1:1, _ in 1:n_hidden])
    b2 ~ Normal(0, 1)
    σ ~ truncated(Normal(0, 1), 0, Inf)
    hidden = σ.(w1 * x .+ b1)
    μ = w2 * hidden .+ b2
    y .~ Normal.(μ, σ)
end

# Run VI
model = bayesian_nn(X, y)
q = vi(model, ADVI(10, 1000))

# Predict
mean_pred, std_pred = predict(q, X[end-50:end, :])
plot(y[end-50:end], label="True Close Price", linewidth=2)
plot!(mean_pred, ribbon=std_pred, label="Predicted Close Price", fillalpha=0.2)
xlabel!("Time")
ylabel!("Close Price")
title!("Crypto Close Price Prediction with Bayesian VI")
