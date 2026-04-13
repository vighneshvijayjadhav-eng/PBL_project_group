import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function StatusChart({ claims }) {
  const statuses = ["approved", "rejected", "pending"];
  const chartData = statuses.map((status) => ({
    name: status,
    count: claims.filter((claim) => claim.status === status).length,
  }));

  return (
    <section className="chart-card">
      <div className="chart-header">
        <p className="eyebrow">Status Breakdown</p>
        <h3>Approved / Rejected / Pending</h3>
      </div>
      <div className="chart-body">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#0f5d84" radius={[10, 10, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default StatusChart;
