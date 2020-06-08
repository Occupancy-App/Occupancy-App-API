/*
 * This app is a collaboration to help business as the open to help keep track of how many occupants they have.
 * The front end is in a different cloudflare worker, this is the backend KV store. The store is broken up as follows:
 * Update Current KV data call -> spaceUpdateHandler
 * Create new KV store -> createSpace
 * Get KV data call -> spaceReturnHandler
 * Contact us form call -> contactUs
 * Fetch event call handlers  ---- Fetch Event calls ----
*/



// Update KV value;
async function spaceUpdateHandler(request) {
    const d = new Date();
    const n = d.toString();
    let data = await SPACE.get(request.id);
        data = JSON.parse(data);
    if(data.password !== false && data.password !== request.password){
      return JSON.stringify({"error": "Incorrect Password"});
    }else{
      if(request.new_val !== 0){
        data.total = Number(data.total) + Number(request.new_val);
        //Possible future option to add who made the last update.
        //data.user_id = request.user_id;
        data.last_update = d;
      }
      if(request.max !== null && request.max !== data.max){
        data.max = request.max;
        data.last_update = d;
      }

      await SPACE.put(request.id, JSON.stringify(data));
      return JSON.stringify(data);
    }
}
//Create new KV store
async function createSpace(request) {
    const key = uuidv4();
    const data = {
      key:key,
      total: request.total ? request.total : 0,
      max:request.max ? request.max : 0,
      password: request.password ? request.password : false
    }
    await SPACE.put(key, JSON.stringify(data));
    return JSON.stringify(data);
}

//Generate unique KV key
function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

//Get KV data call
async function spaceReturnHandler(request) {
  const key = request.id;
  let data = await SPACE.get(key);
      data = JSON.parse(data);
  if(data.password !== false && data.password !== request.password){
    return JSON.stringify({"error": "Incorrect Password"});
  }else{
    return JSON.stringify(data);
  }
}

//Contact us form call
async function contactUs(request){

  const data = {"personalizations":
                    [
                      {
                      "to": [{"email":""}, {"email":""}],
                      "cc":[{"email":request.email}]
                       }
                     ],
                      "from":{"email":""},
                      "subject":"You Recived a message from the ocupancy_app",
                      "content":[{"type":"text/plain","value":request.message}]
                }
  let response = await fetch('https://api.sendgrid.com/v3/mail/send',{
                              "method": "POST",
                              "timeout": 0,
                              "headers": {
                                "Content-Type": ["application/json", "application/json"],
                                "Authorization": "Bearer "
                              },
                              "body":JSON.stringify(data)
                            });
  let message = {'message': "<h2>There was an error processesing the email, please try again later.</h2>"};
  if(response && response.status == 202){
    message = {'message': "<h2>Thank you for contacting us,<br.> we will be in touch as soon as possible!</h2>"}
  }
  return JSON.stringify(message);
}

/*---- Fetch Event calls ----*/
// An example worker which supports CORS. It passes GET and HEAD
// requests through to the origin, but answers OPTIONS and POST
// requests directly. POST requests must contain a JSON payload,
// which is simply echoed back.

addEventListener('fetch', event => {
  event.respondWith(handle(event.request)
    // For ease of debugging, we return exception stack
    // traces in response bodies. You are advised to
    // remove this .catch() in production.
    .catch(e => new Response(e.stack, {
      status: 500,
      statusText: "Internal Server Error"
    }))
  )
})

async function handle(request) {
  if (request.method === "OPTIONS") {
    return handleOptions(request)
  } else if (request.method === "POST") {
    return handlePost(request)
  } else if (request.method === "GET" || request.method == "HEAD") {
    // Pass-through to origin.
    return fetch(request)
  } else {
    return new Response(null, {
      status: 405,
      statusText: "Method Not Allowed",
    })
  }
}

function handleOptions(request) {
  if (request.headers.get("Origin") !== null &&
    request.headers.get("Access-Control-Request-Method") !== null &&
    request.headers.get("Access-Control-Request-Headers") !== null) {
    // Handle CORS pre-flight request.
    return new Response(null, {
      headers: corsHeaders
    })
  } else {
    // Handle standard OPTIONS request.
    return new Response(null, {
      headers: {
        "Allow": "GET, HEAD, POST, OPTIONS",
      }
    })
  }
}

async function handlePost(request) {
  if (request.headers.get("Content-Type") !== "application/json") {
    return new Response(null, {
      status: 415,
      statusText: "Unsupported Media Type",
      headers: corsHeaders,
    })
  }

  // Detect parse failures by setting `json` to null.
  let json = await request.json().catch(e => null)
  if (json === null) {
    return new Response("JSON parse failure", {
      status: 400,
      statusText: "Bad Request",
      headers: corsHeaders,
    })
  }

  // Routes seemed to be causing the main CORS issue,
  // to get around that I send a param with the call I want to make.
  let data = null
  switch (json.call) {
    case "generate":
      data = await createSpace(json)
    break;
    case "update":
      data = await spaceUpdateHandler(json)
    break;
    case "get":
      data = await spaceReturnHandler(json)
    break;
    case "contact":
      data = await contactUs(json)
    break;
    default:
      data = JSON.stringify({"error": "Call Not recognized."});
  }

  return new Response(data, {
    headers: {
      status: 200,
      "Content-Type": "application/json",
      ...corsHeaders,
    }
  })
}

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
}
