import { dates, tiers, data } from "./data.js";

function decompress(str){
    const pako = window.pako;
    var arr = pako.inflate(atob(str));
    var decoder = new TextDecoder();
    return decoder.decode(arr);
}

const num_tiers = tiers.length;
const num_categories = 30;

var results_table = document.getElementById("results-table");

// which user do we need to add to the table next?
var next_user = 0;

for(var i=num_tiers-1; i>=0; i--){
    const tier = tiers[i];

    // table of all results of users in this tier
    var tier_table = document.createElement("table");

    // set up the header rows
    var tier_head = document.createElement("thead"); // header containing the following three rows
    var tier_name_row = document.createElement("tr"); // row containing the name of the tier
    var tier_req_row = document.createElement("tr"); // row containing the results required for the tier
    var tier_events_row = document.createElement("tr"); // row containing names of the categories

    results_table.appendChild(tier_table);
    tier_table.appendChild(tier_head);
    tier_head.appendChild(tier_name_row);
    tier_head.appendChild(tier_req_row);
    tier_head.appendChild(tier_events_row);

    tier_head.className = "sticky";
    tier_req_row.className = "req-row";

    // add the users to the table
    while(true){
        const user = table[next_user];

        // if the user's power is too low, stop adding new rows
        if(user[2] < tier["limit"]){
            break;
        }

        // create a new row and the cells for the username, place, power
        var user_row = document.createElement("tr");
        var name_div = document.createElement("td");
        var place_div = document.createElement("td");
        var power_div = document.createElement("td");

        name_div.textContent = user[0];
        place_div.textContent = user[1];
        power_div.textContent = user[2];

        tier_table.appendChild(user_row);
        user_row.appendChild(name_div);
        user_row.appendChild(place_div);
        user_row.appendChild(power_div);

        next_user++;
    }
}
