import { show_results_from_date } from './populate_table.js';
import { data } from './data.js';

var datepicker = new Datepickk();
var dates = Object.keys(data);
var min_date = dates[0].split("-");
var max_date = dates[dates.length-1].split("-");
datepicker.minDate = new Date(min_date[0], min_date[1]-1, min_date[2]);
datepicker.maxDate = new Date(max_date[0], max_date[1]-1, max_date[2]);
datepicker.currentDate = datepicker.maxDate;
datepicker.maxSelections = 1;
datepicker.title = "Select date:";

datepicker.onSelect = function(checked){
    if(checked){
        var d = this.getDate().toString().padStart(2, "0");
        var m = (this.getMonth()+1).toString().padStart(2, "0");
        var y = this.getFullYear();
        var date = y + "-" + m + "-" + d;
        show_results_from_date(date);
    }
};

window.select_date = function(){
    datepicker.show();
}
