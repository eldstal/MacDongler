
// Hashes of all previously handled status messages
HANDLED_HASHES = {}

// Timestamp of most recent handled status message
LOG_TIMESTAMP = 0

// Running count of successful devices
N_FOUND = 0



// Page elements we will update
mcd_progress_current = document.getElementById("mcd_progress_current")
mcd_progress_target = document.getElementById("mcd_progress_target")

mcd_progress_container = document.getElementById("mcd_progress_container")
mcd_progress_percent = document.getElementById("mcd_progress_percent")

mcd_count_found = document.getElementById("mcd_count_found")
mcd_device_current = document.getElementById("mcd_device_current")

mcd_table_devices = document.getElementById("mcd_table_devices")

mcd_table_errors = document.getElementById("mcd_table_errors")
mcd_table_warnings = document.getElementById("mcd_table_warnings")
mcd_table_log = document.getElementById("mcd_table_log")


function padded_hex(dec) {
  hex = dec.toString(16);
  return hex.padStart(4, '0');
}


function log_message(timestamp, level, text) {

  log_tables = [ mcd_table_log ];
  style = "";

  if (level == "error") {
    log_tables.push(mcd_table_errors);
    style = "table-danger";

  }
  else if (level == "warning") {
    log_tables.push(mcd_table_warnings);
    style = "table-warning";

  }
  else if (level == "found") {
    style = "table-success";
  }
  else if (level == "info") {
    style = "";
  }
  else if (level == "debug") {
    style = "table-secondary";
  }

  date = new Date(timestamp * 1000);
  time_render = `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`

  // It's probably better to do this by building a DOM object,
  // but why? Seems like too much code for something that
  // will be more readable this way...?
  row = `<tr class="${style}">` +
            `<td>${time_render}</td>` +
            `<td>${level}</td>` +
            `<td>${text}</td>` +
        `</tr>`;

  log_tables.forEach(tab => { console.log(tab); console.log(row); tab.innerHTML = row + "\n" + tab.innerHTML; } );

}

function handle_message(msg) {

  log_message(msg["timestamp"], msg["level"], msg["text"])
}


function set_progress(current, target, percent) {
  mcd_progress_percent.innerHTML = `${percent}%`
  mcd_progress_percent.style.width = `${percent}%`
  mcd_progress_container.setAttribute("aria-valuenow", percent)

  mcd_progress_current.innerHTML = `${current}`
  mcd_progress_target.innerHTML = `${target}`

}

function handle_progress(msg) {
  set_progress(msg["current"], msg["target"], msg["percent"]);
}

function handle_current_device(msg) {
  mcd_device_current.innerHTML = `${msg["device_name"]}`
}

function handle_found_device(msg) {
  N_FOUND += 1;

  mcd_count_found.innerHTML = `${N_FOUND}`

  log_message(msg["timestamp"], "found", `Device ${msg["device_name"]} was found to be working!`);

  vid_pid = padded_hex(msg["device_vid"]) + ":" + padded_hex(msg["device_pid"]);

  row = `<tr class="table-success">`+
            `<td>${msg["device_name"]}</td>` +
            `<td>${msg["device_type"]}</td>` +
            `<td>${vid_pid}</td>` +
        `</tr>`

  mcd_table_devices.innerHTML += "\n" + row;
}



function handle_event(msg) {

  if (!("timestamp" in msg)) {
    console.log("This log message is missing a timestamp. Status file probably broken.");
    return;
  }

  if (!("kind" in msg)) {
    console.log("This log message is missing a kind. Status file probably broken.");
    return;
  }

  if (!("hash" in msg)) {
    console.log("This log message is missing a hash. Server script probably broken.");
    return;
  }

  // We've handled this exact message already. Don't duplicate.
  if (msg["hash"] in HANDLED_HASHES) {
    return;
  }

  // Mark this message as dealt with
  HANDLED_HASHES[msg["hash"]] = true;
  LOG_TIMESTAMP = Math.max(LOG_TIMESTAMP, msg["timestamp"])

  switch (msg["kind"]) {

    case "message":
      handle_message(msg);
      break;

    case "progress":
      handle_progress(msg);
      break;

    case "current_device":
      handle_current_device(msg);
      break;

    case "found":
      handle_found_device(msg);
      break;

    default:
      console.log(`Unsupported message type: ${msg["kind"]}. Update the front-end.`)
  }

}

function update_display() {
  fetch(`/status/${LOG_TIMESTAMP}`)
    .then(response => response.json())
    .then(messages => {
      messages.forEach(handle_event)
    })
    .catch(error => {
      // No problem, really.
      // It could be that the MacDongler device is rebooting,
      // so the client here should just stay cool and wait.
    });
}


function auto_update_display() {
  update_display();
  setTimeout(auto_update_display, 1000);
}



/*
 * Clear placeholder values
 */
mcd_table_devices.innerHTML = "";
mcd_table_errors.innerHTML = "";
mcd_table_warnings.innerHTML = "";
mcd_table_log.innerHTML = "";

set_progress(0, 0, 0);

auto_update_display();
