## Cloudflare Occupancy App api

This is the Worker KV used to test Clouflare as a possibility of hosting both ends of our app.

Built using [`Worker KV`](https://developers.cloudflare.com/workers/quickstart)


### Occupancy

The front end is in a different cloudflare worker, this is the backend KV store. The store is broken up as follows:

* Update Current KV data call -> spaceUpdateHandler

 * Used to update the current value + or - value or max value

 * returns space values

* Create new KV store -> createSpace

 * used to create space and return space id number

* Get KV data call -> spaceReturnHandler

  * Used to get data from specific space, no update required.

* Contact us form call -> contactUs

  * calls external service to send us an email.

* Fetch event call handlers  ---- Fetch Event calls ----
