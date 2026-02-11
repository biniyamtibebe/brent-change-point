import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';

const PriceChart = ({ prices, changePoints, events }) => {
  // Convert to chart format, add markers
  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={prices}>
        <Line type="monotone" dataKey="Price" stroke="#8884d8" />
        {changePoints.map(cp => (
          <ReferenceLine key={cp.Date} x={cp.Date} stroke="red" label="Change Point" />
        ))}
        {events.map(ev => (
          <ReferenceLine key={ev.Date} x={ev.Date} stroke="orange" strokeDasharray="3 3" />
        ))}
        <Tooltip />
        <XAxis dataKey="Date" />
        <YAxis />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PriceChart;