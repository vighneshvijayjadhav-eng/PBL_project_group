import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = {
  low: "#4bbf8a",
  medium: "#f2aa3b",
  high: "#de5a53",
};

function RiskChart({ claims }) {
  const chartData = ["low", "medium", "high"].map((riskLevel) => ({
    name: riskLevel,
    value: claims.filter((claim) => claim.risk_level === riskLevel).length,
  }));

  return (
    <section className="chart-card">
      <div className="chart-header">
        <p className="eyebrow">Risk Distribution</p>
        <h3>Low / Medium / High Claims</h3>
      </div>
      <div className="chart-body">
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={88}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={COLORS[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default RiskChart;
