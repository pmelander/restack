# Lockerline: Deployment Guide

**Version:** 2.0

## Order

1. Deploy the queue.
2. Deploy the Booking API with `RESERVE_VIA_QUEUE=true`.
3. Verify that a reservation reaches the Locker Controller within 30 seconds.
