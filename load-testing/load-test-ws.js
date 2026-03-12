import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const BASE_URL = __ENV.WS_URL || 'ws://backend:8000';

export const options = {
  stages: [
    { duration: '5m', target: 50000 }, // Slow ramp to find the breaking point
  ],
  thresholds: {
    // If 95% of connections take > 5s, STOP the test immediately
    'ws_connecting': [{
      threshold: 'p(95)<5000',
      abortOnFail: true,
      delayAbortEval: '10s'
    }],
    'event_latency_ms': [{
      threshold: 'p(95)<50',
      abortOnFail: true,
      delayAbortEval: '10s'
    }],
    // Also track if any connections are outright failing
    'checks': ['rate>0.99'],
  },
};

const eventLatency = new Trend('event_latency_ms');

export default function () {
  const url = `${BASE_URL}/ws/events`;
  const params = { tags: { my_tag: 'event-subscription' } };

  let connected = false;

  const res = ws.connect(url, params, function (socket) {
    socket.on('open', () => {
      //   console.log('Connected to WS');
      connected = true;

      for(let i = 0; i < 8; i++) {
        // 1. Generate random event ID between 1-8
        const eventId = Math.floor(Math.random() * 8) + 1;

        // 2. Send subscribe action
        const payload = JSON.stringify({
          action: 'subscribe',
          eventId: eventId.toString(),
        });

        socket.send(payload);
      }
    });

    // 3. Print any messages received
    socket.on('message', (data) => {
      const msg = JSON.parse(data);
      //   console.log(`VU ${__VU} received message for event: ${msg.eventId || 'unknown'}`);

      if (msg.sentAt && Math.random() < 0.1) {
        // Calculate the delta
        const latency = Date.now() - msg.sentAt * 1000;

        // Record it in k6
        eventLatency.add(latency);
      }
    });

    // socket.on('close', () => console.log('Disconnected'));
    socket.on('error', (e) => {
      connected = false;
    });

    // Keep the connection open for a specific amount of time
    // Without this sleep, the VU would finish the function and close the connection immediately
    sleep(30);
  });

  check(res, {
    'handshake successful': (r) => connected === true,
  });
}