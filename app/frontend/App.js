import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PriceChart from './components/PriceChart';
import EventTimeline from './components/EventTimeline';
import Filters from './components/Filters';

function App() {
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [dateRange, setDateRange] = useState({start: '2015-01-01', end: '2022-09-30'});

  useEffect(() => {
    axios.get('http://localhost:5000/api/prices', {params: dateRange}).then(res => setPrices(res.data));
    axios.get('http://localhost:5000/api/events').then(res => setEvents(res.data));
    axios.get('http://localhost:5000/api/change_points').then(res => setChangePoints(res.data));
  }, [dateRange]);

  return (
    <div>
      <h1>Brent Oil Price Impact Dashboard</h1>
      <Filters dateRange={dateRange} setDateRange={setDateRange} />
      <PriceChart prices={prices} changePoints={changePoints} events={events} />
      <EventTimeline events={events} changePoints={changePoints} />
    </div>
  );
}

export default App;