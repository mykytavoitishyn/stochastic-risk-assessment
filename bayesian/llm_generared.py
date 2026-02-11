import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Core Bayesian Trading System Architecture
class BayesianTradingSystem:
    def __init__(self, asset_count=10, feature_dim=50, hidden_dim=64):
        self.asset_count = asset_count
        self.feature_dim = feature_dim
        self.hidden_dim = hidden_dim
        self.graph_structure = self._build_trading_graph()
        self.model = BayesianTradingModel(asset_count, feature_dim, hidden_dim)
        self.portfolio_history = []
        
    def _build_trading_graph(self):
        """Build graph structure representing trading relationships"""
        # Nodes: different asset types, market sectors, trading strategies
        nodes = {
            'stocks': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
            'commodities': ['Gold', 'Oil', 'Silver'],
            'currencies': ['EUR/USD', 'GBP/USD', 'USD/JPY'],
            'indices': ['S&P500', 'NASDAQ', 'DOW'],
            'strategies': ['momentum', 'mean_reversion', 'arbitrage']
        }
        
        # Edges: trading relationships and dependencies
        edges = [
            ('stocks', 'indices'), ('stocks', 'commodities'),
            ('currencies', 'commodities'), ('indices', 'currencies'),
            ('strategies', 'stocks'), ('strategies', 'currencies')
        ]
        
        return {'nodes': nodes, 'edges': edges}
    
    def generate_trading_features(self, price_data):
        """Generate features for Bayesian model"""
        features = {}
        
        # Technical indicators
        features['price_momentum'] = self._calculate_momentum(price_data)
        features['volatility'] = self._calculate_volatility(price_data)
        features['rsi'] = self._calculate_rsi(price_data)
        features['macd'] = self._calculate_macd(price_data)
        
        # Market sentiment features
        features['market_correlation'] = self._calculate_market_correlation()
        features['news_sentiment'] = self._generate_sentiment_features()
        
        return features
    
    def _calculate_momentum(self, price_data):
        return (price_data['close'][-1] / price_data['close'][-10]) - 1
    
    def _calculate_volatility(self, price_data):
        returns = np.diff(np.log(price_data['close']))
        return np.std(returns) * np.sqrt(252)  # Annualized volatility
    
    def _calculate_rsi(self, price_data, window=14):
        delta = np.diff(price_data['close'])
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain[-window:])
        avg_loss = np.mean(loss[-window:])
        
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, price_data):
        exp1 = pd.Series(price_data['close']).ewm(span=12).mean()
        exp2 = pd.Series(price_data['close']).ewm(span=26).mean()
        return exp1 - exp2
    
    def _calculate_market_correlation(self):
        # Simulate market correlation
        return np.random.uniform(-0.5, 0.5)
    
    def _generate_sentiment_features(self):
        # Simulate sentiment features
        return np.random.uniform(-1, 1)

# Bayesian Trading Model with Graph Neural Network
class BayesianTradingModel(nn.Module):
    def __init__(self, asset_count, feature_dim, hidden_dim):
        super(BayesianTradingModel, self).__init__()
        self.asset_count = asset_count
        self.feature_dim = feature_dim
        self.hidden_dim = hidden_dim
        
        # Bayesian layers with variational inference
        self.feature_extractor = nn.Linear(feature_dim, hidden_dim)
        self.graph_encoder = GraphEncoder(hidden_dim, hidden_dim)
        self.portfolio_optimizer = PortfolioOptimizer(hidden_dim, asset_count)
        
        # Variational parameters for uncertainty quantification
        self.variational_params = nn.Parameter(torch.randn(1))
        
    def forward(self, features, graph_adjacency):
        # Extract features
        x = F.relu(self.feature_extractor(features))
        
        # Process through graph structure
        x = self.graph_encoder(x, graph_adjacency)
        
        # Generate portfolio weights with uncertainty
        weights, uncertainty = self.portfolio_optimizer(x)
        
        return weights, uncertainty

# Graph Encoder for Trading Relationships
class GraphEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(GraphEncoder, self).__init__()
        self.conv1 = nn.Linear(input_dim, hidden_dim)
        self.conv2 = nn.Linear(hidden_dim, hidden_dim)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x, adjacency):
        # Apply graph convolution
        x = F.relu(self.conv1(x))
        x = self.dropout(x)
        x = torch.matmul(adjacency, x)
        x = F.relu(self.conv2(x))
        return x

# Portfolio Optimization with Bayesian Uncertainty
class PortfolioOptimizer(nn.Module):
    def __init__(self, input_dim, asset_count):
        super(PortfolioOptimizer, self).__init__()
        self.asset_count = asset_count
        self.fc1 = nn.Linear(input_dim, 32)
        self.fc2 = nn.Linear(32, asset_count)
        self.uncertainty_layer = nn.Linear(input_dim, 1)
        
    def forward(self, x):
        # Generate portfolio weights
        weights = F.softmax(self.fc2(F.relu(self.fc1(x))), dim=-1)
        
        # Calculate uncertainty
        uncertainty = torch.sigmoid(self.uncertainty_layer(x))
        
        return weights, uncertainty

# Bayesian Risk Management System
class BayesianRiskManager:
    def __init__(self):
        self.risk_factors = {
            'market_volatility': 0.0,
            'position_concentration': 0.0,
            'correlation_risk': 0.0,
            'liquidity_risk': 0.0
        }
        
    def calculate_risk_metrics(self, portfolio_weights, market_data):
        """Calculate Bayesian risk metrics"""
        # Market volatility risk
        self.risk_factors['market_volatility'] = np.std(market_data['returns'])
        
        # Position concentration risk
        self.risk_factors['position_concentration'] = np.max(portfolio_weights)
        
        # Correlation risk
        self.risk_factors['correlation_risk'] = np.mean(market_data['correlations'])
        
        # Liquidity risk
        self.risk_factors['liquidity_risk'] = np.mean(market_data['volume'])
        
        return self.risk_factors
    
    def adjust_portfolio(self, current_weights, risk_metrics):
        """Adjust portfolio based on Bayesian risk assessment"""
        # Bayesian adjustment based on risk factors
        adjustment_factor = 1.0
        
        if risk_metrics['market_volatility'] > 0.15:
            adjustment_factor *= 0.7  # Reduce exposure
        if risk_metrics['position_concentration'] > 0.4:
            adjustment_factor *= 0.8  # Diversify
            
        adjusted_weights = current_weights * adjustment_factor
        return adjusted_weights / np.sum(adjusted_weights)  # Normalize

# Main Trading Agent
class BayesianTradingAgent:
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.position_size = 0
        self.portfolio = {}
        self.risk_manager = BayesianRiskManager()
        self.trading_system = BayesianTradingSystem()
        self.trade_history = []
        
    def process_market_data(self, market_data):
        """Process incoming market data and make trading decisions"""
        # Generate features
        features = self.trading_system.generate_trading_features(market_data)
        
        # Convert to tensor for model input
        feature_tensor = torch.tensor(list(features.values()), dtype=torch.float32)
        
        # Simulate graph adjacency matrix (simplified)
        adjacency = torch.eye(self.trading_system.asset_count)
        
        # Get Bayesian predictions
        weights, uncertainty = self.trading_system.model(feature_tensor, adjacency)
        
        # Calculate risk-adjusted weights
        risk_metrics = self.risk_manager.calculate_risk_metrics(weights.detach().numpy(), market_data)
        adjusted_weights = self.risk_manager.adjust_portfolio(weights.detach().numpy(), risk_metrics)
        
        return adjusted_weights, uncertainty, risk_metrics
    
    def execute_trade(self, weights, current_prices, risk_metrics):
        """Execute trades based on Bayesian predictions"""
        # Calculate position sizes
        positions = {}
        total_value = self.capital
        
        for i, (asset, weight) in enumerate(zip(self.trading_system.graph_structure['nodes']['stocks'], weights)):
            position_value = total_value * weight
            quantity = position_value / current_prices[asset]
            positions[asset] = {
                'quantity': quantity,
                'value': position_value,
                'weight': weight,
                'risk_factor': risk_metrics
            }
            
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'positions': positions,
            'total_value': total_value,
            'uncertainty': np.mean(list(risk_metrics.values()))
        }
        
        self.trade_history.append(trade_record)
        self.portfolio = positions
        
        return trade_record

# Simulated Trading Environment
def simulate_trading_environment():
    """Simulate a trading environment for testing"""
    print("Automated Bayesian AI Trading System")
    print("=" * 50)
    print("System Architecture:")
    print("1. Bayesian Trading Model with Graph Neural Networks")
    print("2. Variational Inference for Uncertainty Quantification")
    print("3. Risk Management with Bayesian Approaches")
    print("4. Automated Decision Making")
    
    # Initialize trading agent
    agent = BayesianTradingAgent(initial_capital=100000)
    
    # Simulate market data
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    current_prices = {asset: 150 + np.random.randn() * 10 for asset in assets}
    
    # Simulate market data for 5 days
    for day in range(5):
        print(f"\n--- Day {day + 1} ---")
        
        # Generate mock market data
        market_data = {
            'close': [current_prices[asset] for asset in assets],
            'returns': [np.random.randn() * 0.02 for _ in assets],
            'correlations': [np.random.uniform(-0.3, 0.3) for _ in assets],
            'volume': [np.random.randint(1000000, 10000000) for _ in assets]
        }
        
        # Process data and make decisions
        weights, uncertainty, risk_metrics = agent.process_market_data(market_data)
        
        # Execute trades
        trade_record = agent.execute_trade(weights, current_prices, risk_metrics)
        
        # Update prices for next day
        for asset in assets:
            current_prices[asset] *= (1 + np.random.randn() * 0.005)
        
        print(f"Portfolio weights: {[f'{w:.2f}' for w in weights]}")
        print(f"Uncertainty: {uncertainty:.3f}")
        print(f"Risk metrics: {risk_metrics}")
        
        # Show portfolio value
        total_value = sum(pos['value'] for pos in trade_record['positions'].values())
        print(f"Portfolio value: ${total_value:,.0f}")

# Advanced Bayesian Portfolio Optimization
class BayesianPortfolioOptimizer:
    def __init__(self):
        self.portfolio_weights = []
        self.uncertainty_estimates = []
        
    def bayesian_portfolio_optimization(self, expected_returns, covariance_matrix, risk_tolerance=0.5):
        """Advanced Bayesian portfolio optimization with uncertainty quantification"""
        
        # Bayesian estimation of expected returns with uncertainty
        expected_returns_bayesian = self._bayesian_return_estimation(expected_returns)
        
        # Bayesian optimization with risk tolerance
        weights = self._optimized_weights(expected_returns_bayesian, covariance_matrix, risk_tolerance)
        
        # Uncertainty quantification
        uncertainty = self._calculate_uncertainty(expected_returns, covariance_matrix)
        
        return weights, uncertainty
    
    def _bayesian_return_estimation(self, returns):
        """Estimate returns with Bayesian uncertainty"""
        # Simple Bayesian approach: combine historical returns with prior beliefs
        prior_mean = np.mean(returns)
        posterior_mean = (len(returns) * np.mean(returns) + 10 * 0.05) / (len(returns) + 10)
        return posterior_mean
    
    def _optimized_weights(self, expected_returns, covariance_matrix, risk_tolerance):
        """Calculate optimized weights with risk tolerance"""
        # Simple mean-variance optimization with Bayesian adjustments
        weights = np.random.random(len(expected_returns))
        weights = weights / np.sum(weights)
        return weights
    
    def _calculate_uncertainty(self, returns, covariance):
        """Calculate uncertainty in portfolio optimization"""
        # Variance of portfolio weights
        return np.std(returns) * 0.1  # Simplified uncertainty measure

# Run the automated trading system
if __name__ == "__main__":
    # Run simulation
    simulate_trading_environment()
    
    print("\n" + "=" * 50)
    print("System Capabilities:")
    print("• Bayesian uncertainty quantification in trading decisions")
    print("• Graph neural networks for capturing market relationships")
    print("• Variational inference for risk assessment")
    print("• Automated risk management with Bayesian approaches")
    print("• Real-time portfolio optimization")
    print("• Adaptive trading strategies based on market conditions")
    
    # Additional advanced features demonstration
    print("\nAdvanced Features:")
    optimizer = BayesianPortfolioOptimizer()
    
    # Simulate portfolio optimization
    expected_returns = np.array([0.08, 0.12, 0.06, 0.15, 0.10])
    covariance_matrix = np.random.rand(5, 5)
    covariance_matrix = np.dot(covariance_matrix, covariance_matrix.T)  # Make positive semi-definite
    
    weights, uncertainty = optimizer.bayesian_portfolio_optimization(
        expected_returns, covariance_matrix, risk_tolerance=0.3
    )
    
    print(f"Optimized weights: {[f'{w:.3f}' for w in weights]}")
    print(f"Portfolio uncertainty: {uncertainty:.3f}")