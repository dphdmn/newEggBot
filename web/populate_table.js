import { dates, data } from "./data.js";

const tiers = ["gamma", "aleph", "ascended", "nova", "grandmaster", "master", "diamond", "platinum", "gold", "silver", "bronze", "beginner", "unranked"];
const num_tiers = tiers.length;
const num_categories = 30;

var results_table = document.getElementById("results-table");

for(var i=0; i<num_tiers; i++){
    // tier name
    var tier = tiers[i];

    // table of all results of users in this tier
    var tier_table = document.createElement("table");

    // set up the rows
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
}
