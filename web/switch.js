let tierlist = ["gamma", "aleph", "ascended", "nova", "grandmaster", "master", "diamond", "platinum", "gold", "silver", "bronze", "beginner"];
let switchBtn = $("#switch");

switchBtn.on('change', function() {
    tierlist.forEach((tier) => {
        changeTable(tier);
    });
});

function changeTable(tier_table) {
  let elements = $(`#${tier_table}-table`).children($("tbody")).children(".player-row").children();
  
  $(elements).each((i) => {
    let element = $(elements[i]);
    let tier = element.attr("tier");

    if (tier) {
        if (tierlist.indexOf(tier) <= tierlist.indexOf(tier_table)) {
            if (tierlist.indexOf(tier) < tierlist.indexOf(tier_table)) {
                if (switchBtn.is(':checked')) {
                    $(element).css("font-weight", 800);
                } else {
                    $(element).css("font-weight", "");
                }
            }
        } else {
            if (switchBtn.is(':checked')) {
                $(element).css("background-color", "grey");
            } else {
              $(element).css("background-color", "");

            }
        }
    }
  });
}

