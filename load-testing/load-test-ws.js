import ws from 'k6/ws';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.WS_URL || 'ws://backend:8000';

export const options = {
  stages: [
    { duration: '5s', target: 10000 },  // Ramp up to 50 concurrent users
    { duration: '10s', target: 10000 },   // Stay at 50 users
    { duration: '5s', target: 0 },   // Ramp down
  ],
//   thresholds: {
//     'stopped_connecting': ['count<10'], // Monitor connection drops
//   },
};

export default function () {
  const url = `${BASE_URL}/ws/events`;
  const params = { tags: { my_tag: 'event-subscription' } };

  const res = ws.connect(url, params, function (socket) {
    socket.on('open', () => {
      console.log('Connected to WS');

      // 1. Generate random event ID between 1-8
      const eventId = Math.floor(Math.random() * 8) + 1;

      // 2. Send subscribe action
      const payload = JSON.stringify({
        action: 'subscribe',
        eventId: eventId.toString(),
      });
      
      socket.send(payload);
    });

    // 3. Print any messages received
    socket.on('message', (data) => {
      const msg = JSON.parse(data);
    //   console.log(`VU ${__VU} received message for event: ${msg.eventId || 'unknown'}`);
    });

    socket.on('close', () => console.log('Disconnected'));
    socket.on('error', (e) => console.log('WS Error: ', e.error()));

    // Keep the connection open for a specific amount of time
    // Without this sleep, the VU would finish the function and close the connection immediately
    sleep(10); 
  });

  check(res, { 'status is 101': (r) => r && r.status === 101 });
}