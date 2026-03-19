import {
  ComposedChart,
  LineChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

const fmtDate = (ts) => {
  const d = new Date(ts);
  return `${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
};

const fmtTooltipDate = (ts) => {
  if (!ts) return "";
  const d = new Date(ts);
  return d.toLocaleString();
};

const fmtPrice = (v) => (v ? `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : "");

export function PriceChart({ chartData, tradeMarkers }) {
  const buyPoints = tradeMarkers.filter((m) => m.type === "buy");
  const sellPoints = tradeMarkers.filter((m) => m.type === "sell");

  return (
    <div className="chart-block">
      <h3>Price + Moving Averages</h3>
      <ResponsiveContainer width="100%" height={260}>
        <ComposedChart data={chartData} margin={{ right: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="date"
            type="number"
            scale="time"
            domain={["auto", "auto"]}
            tickFormatter={fmtDate}
            tick={{ fontSize: 10, fill: "#8b949e" }}
            tickCount={6}
          />
          <YAxis
            domain={["auto", "auto"]}
            tickFormatter={fmtPrice}
            tick={{ fontSize: 10, fill: "#8b949e" }}
            width={70}
          />
          <Tooltip
            labelFormatter={fmtTooltipDate}
            formatter={(v, name) => [v ? `$${v.toLocaleString()}` : "—", name]}
            contentStyle={{ background: "#161b22", border: "1px solid #30363d", fontSize: 11 }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line dataKey="close" stroke="#e6edf3" dot={false} strokeWidth={1.5} name="Price" />
          <Line dataKey="ma_short" stroke="#58a6ff" dot={false} strokeWidth={1} name="MA Short" />
          <Line dataKey="ma_long" stroke="#d2a8ff" dot={false} strokeWidth={1} name="MA Long" />
          <Line dataKey="ma_trend" stroke="#ffa657" dot={false} strokeWidth={1} name="MA Trend" />
          <Scatter
            data={buyPoints}
            dataKey="price"
            fill="#3fb950"
            name="Buy entry"
            xAxisId={0}
            yAxisId={0}
            shape={<TriangleUp />}
          />
          <Scatter
            data={sellPoints}
            dataKey="price"
            fill="#f85149"
            name="Sell entry"
            xAxisId={0}
            yAxisId={0}
            shape={<TriangleDown />}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function TriangleUp({ cx, cy }) {
  if (!cx || !cy) return null;
  return <polygon points={`${cx},${cy - 7} ${cx - 5},${cy + 3} ${cx + 5},${cy + 3}`} fill="#3fb950" />;
}

function TriangleDown({ cx, cy }) {
  if (!cx || !cy) return null;
  return <polygon points={`${cx},${cy + 7} ${cx - 5},${cy - 3} ${cx + 5},${cy - 3}`} fill="#f85149" />;
}

export function RSIChart({ chartData }) {
  return (
    <div className="chart-block">
      <h3>RSI-14</h3>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={chartData} margin={{ right: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="date"
            type="number"
            scale="time"
            domain={["auto", "auto"]}
            tickFormatter={fmtDate}
            tick={{ fontSize: 10, fill: "#8b949e" }}
            tickCount={6}
          />
          <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#8b949e" }} width={30} />
          <Tooltip
            labelFormatter={fmtTooltipDate}
            formatter={(v) => [v?.toFixed(1), "RSI"]}
            contentStyle={{ background: "#161b22", border: "1px solid #30363d", fontSize: 11 }}
          />
          <ReferenceLine y={70} stroke="#f85149" strokeDasharray="4 4" strokeOpacity={0.6} />
          <ReferenceLine y={30} stroke="#3fb950" strokeDasharray="4 4" strokeOpacity={0.6} />
          <Line dataKey="rsi" stroke="#ffa657" dot={false} strokeWidth={1.5} name="RSI" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PortfolioChart({ portfolioCurve, initPortfolio }) {
  if (!portfolioCurve || portfolioCurve.length === 0) return null;

  const startPoint = { date: portfolioCurve[0].date, portfolio: initPortfolio };
  const data = [startPoint, ...portfolioCurve];

  return (
    <div className="chart-block">
      <h3>Portfolio Equity Curve</h3>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ right: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="date"
            type="number"
            scale="time"
            domain={["auto", "auto"]}
            tickFormatter={fmtDate}
            tick={{ fontSize: 10, fill: "#8b949e" }}
            tickCount={6}
          />
          <YAxis
            domain={["auto", "auto"]}
            tickFormatter={(v) => `$${v.toLocaleString()}`}
            tick={{ fontSize: 10, fill: "#8b949e" }}
            width={70}
          />
          <Tooltip
            labelFormatter={fmtTooltipDate}
            formatter={(v) => [`$${v.toLocaleString()}`, "Portfolio"]}
            contentStyle={{ background: "#161b22", border: "1px solid #30363d", fontSize: 11 }}
          />
          <ReferenceLine y={initPortfolio} stroke="#8b949e" strokeDasharray="4 4" strokeOpacity={0.5} />
          <Line
            dataKey="portfolio"
            stroke="#58a6ff"
            dot={{ r: 3, fill: "#58a6ff" }}
            strokeWidth={1.5}
            name="Portfolio"
            type="stepAfter"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
