// ------------------------------------------------------------------------------
// Get the items:
// ------------------------------------------------------------------------------
const t = document.getElementById("table1");
const login_btn = document.getElementById("log_btn");
const fetch_data_btn = document.getElementById("get_btn");

const loader_box = document.getElementById("loader");
const main_box = document.getElementById("main");

// ------------------------------------------------------------------------------
// Loader:
// ------------------------------------------------------------------------------
window.onload = function () {
    // Show loader till the page is visible:
    loader_box.style.display = "none";
    main_box.style.display = "block";
};

// ------------------------------------------------------------------------------
// Event listeners:
// ------------------------------------------------------------------------------
const ideal_mode = true;

// When login in pressed, fetch the resp from /login endpoint, save resp json in variable:
login_btn.addEventListener("click", () => {
    loader_box.style.display = "block";
    fetch("/login")
        .then(resp => resp.json())
        .then(data => {
            // console.log(data);

            if (data.status == false) {
                console.log("Login failed! \n" + data.message);
                alert("Login failed! \n" + data.message);
            } else {
                console.log("Login successful! \n" + data.message);
                alert("Login successful! \n" + data.message);
            }

            loader_box.style.display = "none";
        });
});


// When fetch data is pressed, fetch the resp from /get_data endpoint, 
fetch_data_btn.addEventListener("click", () => {
    loader_box.style.display = "block";
    fetch(`/get_data?ideal_mode=${ideal_mode}`)
        .then(resp => resp.json())
        .then(data => {
            console.log(data);

            if (data.status == false) {
                alert("Fetch failed! \n" + data.message);
            } else {
                var obj = pre_process_response(data.message);
                append_in_table(obj);
            }

            loader_box.style.display = "none";
        });
});


// ------------------------------------------------------------------------------
// Functions:
// ------------------------------------------------------------------------------

function add_row(sr, stamp, temp, hum, feel, m1, m4) {
    t.innerHTML += `
    <tr>
        <td>${sr}</td>
        <td>${stamp}</td>
        <td>${temp}</td>
        <td>${hum}</td>
        <td>${feel}</td>
        <td>${m1}</td>
        <td>${m4}</td> 
    </tr>
    `;
}


function pre_process_response(response_node) {

    // Check if the reading is a number and not NaN
    function isValidReading(reading) {
        return typeof reading === "object" &&
            !isNaN(reading.temp) &&
            !isNaN(reading.hum) &&
            !isNaN(reading.feel) &&
            !isNaN(reading.mq135) &&
            !isNaN(reading.mq4);
    }

    var bs_temp = [];
    var bs_hum = [];
    var bs_feel = [];
    var bs_mq135 = [];
    var bs_mq4 = [];
    var bs_keys = [];

    var bs_gas = response_node["gas_node"];
    var bs_fire = response_node["fire_node"];

    // Initialize last valid reading
    var lastValidReading = null;

    for (const key in response_node) {
        if (key !== "fire_node" && key !== "gas_node") {
            bs_keys.push(key);

            const currentReading = response_node[key];
            // Check if the current reading is valid (not undefined, NaN, or any other invalid value)
            if (isValidReading(currentReading)) {
                // Use the current reading
                bs_temp.push(currentReading.temp);
                bs_hum.push(currentReading.hum);
                bs_feel.push(currentReading.feel);
                bs_mq135.push(currentReading.mq135);
                bs_mq4.push(currentReading.mq4);
                lastValidReading = currentReading; // Update last valid reading
            }
            else {
                // Use the last valid reading if available
                if (lastValidReading !== null) {
                    bs_temp.push(lastValidReading.temp);
                    bs_hum.push(lastValidReading.hum);
                    bs_feel.push(lastValidReading.feel);
                    bs_mq135.push(lastValidReading.mq135);
                    bs_mq4.push(lastValidReading.mq4);
                }
                else {
                    // If no valid readings encountered yet, use default values:
                    bs_temp.push(33);
                    bs_hum.push(67);
                    bs_feel.push(39);
                    bs_mq135.push(130);
                    bs_mq4.push(153);
                }
            }
        }
    }

    // Return the result object
    return {
        bs_temp: bs_temp,
        bs_hum: bs_hum,
        bs_feel: bs_feel,
        bs_mq135: bs_mq135,
        bs_mq4: bs_mq4,
        bs_keys: bs_keys,
        bs_gas: bs_gas,
        bs_fire: bs_fire,
        total_length: bs_temp.length
    };
}

function append_in_table(obj) {
    for (let i = 0; i < obj.total_length; i++) {
        // add_row((i + 1), obj.bs_keys[i], obj.bs_temp[i], obj.bs_hum[i], obj.bs_feel[i], obj.bs_mq135[i], obj.bs_mq4[i]);
        add_row(sr = (i + 1),
            temp = obj.bs_temp[i], hum = obj.bs_hum[i], feel = obj.bs_feel[i],
            stamp = obj.bs_keys[i], m1 = obj.bs_mq135[i], m4 = obj.bs_mq4[i]
        )
    }
}
