let table_name_route_info = "routeinfo" // the database table that contains the stations data
let table_name_login = "login" // the database table that contains the login data
let museum_id = "" // saves the uniqe identifier of the museum, by which data will be pulled from the database
let map_data // saves all the changes that accured in the current tour table
let last_selected_station // saves the last station that the user selected 
// pattern to ensure that the first letter that the user enters will be letter in english or number 
let textarea_pattern = /^([A-Za-z0-9]{1,})/ 
// a message to show the user on wrong pattern
let pattern_alert_massage = "must start with one of these characters: Uppercase or lowercase English letters or numbers" 

//A variable that represents the connection to the database
const DB_connention = axios.create({
    baseURL:
        "https://museumrobot-66ba.restdb.io/rest",
    headers: { "x-apikey": "5f58ea37c5e01c1e033b8dbf" }
});


/**
 * A function that pulls from the database all the station names by specified museum_id,
 * initializes the variable datalist_tag with those names.
 */
async function main() {
    document.getElementById("div_menu_btns").style.display = "block"
    const { data } = await DB_connention.get(`/${table_name_route_info}?q={"museum_id":"${museum_id}"}&h={"$fields": {"_id": 1,"station_name": 1} }&sort=station_name&dir=1`)
    var datalist_tag = document.getElementById("stationId")
    datalist_tag.innerHTML = ""
    //loop to initialize datalist_tag
    data.forEach(element => {
        var station_name = document.createElement('option');
        station_name.setAttribute("station_id", element._id);
        station_name.setAttribute("station_name", element.station_name);
        station_name.setAttribute("value", element.station_name);
        datalist_tag.appendChild(station_name)
    })
    stop_loading_animation("all_body", "block")


}

/**
 * A function that checks whether or not text fit to regular expression pattern
 */
function text_fit_pattern(pattern, text) {
    return pattern.test(text)


}

/**
 * A function that displays the data of the selected station
 */
async function display_station_content() {
    let station_name_input = document.getElementById("choose_station_input")
    let station_name_input_value = station_name_input.value
    station_name_input.value = ""
    var div_tag = document.getElementById("station_content")
    //Pulls the appropriate element, according to the user's choice
    let station_option = document.querySelector('option[station_name="' + station_name_input_value + '"]')
    //Displays an error in case there is no suitable element for user selection
    if (station_option == null) {
        show_popup_message("please choose a valid station name");
        return
    }

    if (last_selected_station == station_name_input_value) {
        return
    }
    last_selected_station = station_name_input_value

    div_tag.style.display = "none"
    var record_id_for_url = station_option.attributes.station_id.nodeValue;
    start_loading_animation("block_user_clicks", "block")
    //Pulls from the database, the station data selected by the user
    const { data } = await DB_connention.get(`/${table_name_route_info + "/" + record_id_for_url}?q={}&h={"$fields": {"station_name": 1,"child_content": 1,"adult_content": 1,"play_child": 1 ,"play_adult": 1 ,"current_tour": 1} }`)
    for (let key in data) {

        if (key == "play_child" || key == "play_adult" || key == "current_tour") {
            var tag_to_add_data_to = document.getElementById(key)
            tag_to_add_data_to.checked = data[key]
        }
        else if (key == "child_content" || key == "adult_content" || key == "station_name") {
            var tag_to_add_data_to = document.getElementById(key)
            tag_to_add_data_to.value = data[key]
        }
    }
    document.getElementById("create_new_station_btn").style.display = "none"
    document.getElementById("update_station_btn").style.display = "inline"
    document.getElementById("delete_station_btn").style.display = "inline"
    div_tag.style.display = "block"
    stop_loading_animation("block_user_clicks", "none")
}


/**
* A function that updates the database with the new station data entered by the user
*/
async function update_station() {

    let station_option = document.querySelector('option[station_name="' + last_selected_station + '"]')
    var record_id_for_url = station_option.attributes.station_id.nodeValue;
    var textarea_station_name = document.getElementById("station_name")
    var textarea_child_content = document.getElementById("child_content")
    var textarea_adult_content = document.getElementById("adult_content")
    var checkbox_play_adult = document.getElementById("play_adult")
    var checkbox_play_child = document.getElementById("play_child")
    var checkbox_current_tour = document.getElementById("current_tour")

    if (!(text_fit_pattern(textarea_pattern, textarea_station_name.value))) {
        show_popup_message("station name " + pattern_alert_massage );
        return
    }
    if (!(text_fit_pattern(textarea_pattern, textarea_child_content.value))) {
        show_popup_message("child content " + pattern_alert_massage);
        return
    }
    if (!(text_fit_pattern(textarea_pattern, textarea_adult_content.value))) {
        show_popup_message("adult content " + pattern_alert_massage);
        return
    }

    if (checkbox_current_tour.checked) {
        if (!(checkbox_play_adult.checked || checkbox_play_child.checked)) {
            show_popup_message("please choose atleast one type of conntent to be played");
            return
        }
    }





    start_loading_animation("block_user_clicks", "block")

    //pull the station name entered by the user from the database
    const { data } = await DB_connention.get(`/${table_name_route_info}?q={"museum_id":"${museum_id}" , "station_name": "${textarea_station_name.value}"}`)

    //Displays an error if the station name already exists in the database, not including the current station name
    if (data.length > 0 && textarea_station_name.value != last_selected_station) {
        show_popup_message("station name already taken")
        stop_loading_animation("block_user_clicks", "none")
        return
    }

    //Update the station data in the database, according to the new data entered by the user
    DB_connention.request({
        url: table_name_route_info + "/" + record_id_for_url,
        method: "put",
        data: {
            station_name: textarea_station_name.value,
            child_content: textarea_child_content.value,
            adult_content: textarea_adult_content.value,
            play_adult: checkbox_play_adult.checked,
            play_child: checkbox_play_child.checked,
            current_tour: checkbox_current_tour.checked,
        }
    }).then(response => {
        block_user_clicks.style.display = "none"
        stop_loading_animation("block_user_clicks", "none")
        if (response.status == 200) {
            station_option.value = textarea_station_name.value
            station_option.attributes.station_name.nodeValue = textarea_station_name.value
            document.getElementById("station_content").style.display = "none"
            document.getElementById("choose_station_input").value = ""
            last_selected_station = ""

            show_popup_message("station updated successfully")

        }
        else {
            show_popup_message("something went wrong please try again");
        }

    });

}


/**
* A function that deletes the station selected by the user
*/
async function delete_station() {
    start_loading_animation("block_user_clicks", "block")
    let station_option = document.querySelector('option[station_name="' + last_selected_station + '"]')
    var record_id_for_url = station_option.attributes.station_id.nodeValue;


    var datalist = document.getElementById("stationId")
    var div_tag = document.getElementById("station_content")
    //deletes the station selected by the user in the database
    DB_connention.request({
        url: table_name_route_info + "/" + record_id_for_url,
        method: "delete"
    }).then(response => {
        stop_loading_animation("block_user_clicks", "none")
        if (response.status == 200) {
            datalist.removeChild(station_option)
            div_tag.style.display = "none"
            document.getElementById("choose_station_input").value = ""
            last_selected_station = ""

            show_popup_message("station deleted successfully")
        }
        else {
            show_popup_message("something went wrong please try again");
        }

    });


}


/**
* A function that checks the validity of the entered station name, before adding the station to the database
*/
async function create_new_station_data_validation() {
    let textarea_station_name = document.getElementById("station_name")
    let textarea_child_content = document.getElementById("child_content")
    let textarea_adult_content = document.getElementById("adult_content")
    let checkbox_play_adult = document.getElementById("play_adult")
    let checkbox_play_child = document.getElementById("play_child")
    let checkbox_current_tour = document.getElementById("current_tour")

    if (!(text_fit_pattern(textarea_pattern, station_name.value))) {
        show_popup_message("station name " + pattern_alert_massage);
        return
    }
    if (!(text_fit_pattern(textarea_pattern, textarea_child_content.value))) {
        show_popup_message("child content " + pattern_alert_massage);
        return
    }
    if (!(text_fit_pattern(textarea_pattern, textarea_adult_content.value))) {
        show_popup_message("adult content " + pattern_alert_massage);
        return
    }
    if (checkbox_current_tour.checked) {
        if (!(checkbox_play_adult.checked || checkbox_play_child.checked)) {
            show_popup_message("please choose atleast one type of conntent to be played");
            return
        }
    }


    start_loading_animation("block_user_clicks", "block")

    //Check with the database whether the station name already exists
    const { data } = await DB_connention.get(`/${table_name_route_info}?q={"museum_id":"${museum_id}" , "station_name": "${textarea_station_name.value}"}`)
    if (data.length > 0) {
        show_popup_message("station name already taken")
        stop_loading_animation("block_user_clicks", "none")
        return
    }
    create_new_station(textarea_station_name.value);
}

/**
* A function that displays a form for the user,
* to fill in the details of the new station that will be added to the database
*/
function display_new_station_form() {
    var div_tag = document.getElementById("station_content")
    div_tag.style.display = "block"
    document.getElementById("choose_station_input").value = ""

    document.getElementById("station_name").value = ""
    document.getElementById("child_content").value = ""
    document.getElementById("adult_content").value = ""
    document.getElementById("play_child").checked = false
    document.getElementById("play_adult").checked = false
    document.getElementById("current_tour").checked = false




    document.getElementById("create_new_station_btn").style.display = "inline"
    document.getElementById("update_station_btn").style.display = "none"
    document.getElementById("delete_station_btn").style.display = "none"

    last_selected_station = ""

}


/**
* A function that adds to the database the data of the new station filled in by the user
*/
function create_new_station(station_name) {

    let textarea_child_content = document.getElementById("child_content")
    let textarea_adult_content = document.getElementById("adult_content")
    let checkbox_play_adult = document.getElementById("play_adult")
    let checkbox_play_child = document.getElementById("play_child")
    let checkbox_current_tour = document.getElementById("current_tour")

    if (!(text_fit_pattern(textarea_pattern, station_name.value))) {
        show_popup_message("station_name error pattern");
        return
    }
    if (!(text_fit_pattern(textarea_pattern, textarea_child_content.value))) {
        show_popup_message("textarea_child_content error pattern");
        return
    }
    if (!(text_fit_pattern(textarea_pattern, textarea_adult_content.value))) {
        show_popup_message("textarea_adult_content error pattern");
        return
    }

    //Adding the new station data to the database
    DB_connention.request({
        url: table_name_route_info,
        method: "post",
        data: {
            play_adult: checkbox_play_adult.checked,
            play_child: checkbox_play_child.checked,
            current_tour: checkbox_current_tour.checked,
            station_name: station_name,
            child_content: textarea_child_content.value,
            adult_content: textarea_adult_content.value,
            museum_id: museum_id


        }
    }).then(response => {

        if (response.status == 201) {
            var datalist_tag = document.getElementById("stationId");
            var div_tag = document.getElementById("station_content")

            let station_name = document.createElement("OPTION");
            station_name.setAttribute("station_id", response.data._id);
            station_name.setAttribute("station_name", response.data.station_name);
            station_name.setAttribute("value", response.data.station_name);
            datalist_tag.appendChild(station_name)
            sort_datalist("stationId")
            div_tag.style.display = "none"
            stop_loading_animation("block_user_clicks", "none")
            show_popup_message("station saved successfully");

        }
        else {
            stop_loading_animation("block_user_clicks", "none")
            show_popup_message("something went wrong please try again");

        }

    })

}


/**
 * A function that performs authentication for the user's login on the site
 */
async function user_login() {
    let input_user_name_password = document.getElementsByClassName("user_name_password")
    //Checking the compatibility of the username and password entered by the user with the database
    const { data } = await DB_connention.get(`/${table_name_login}?q={"user name":"${input_user_name_password[0].value}" ,"password" : "${input_user_name_password[1].value}"}`)
    if (data.length == 1) {
        document.getElementById("id01").style.display = "none"
        document.getElementById("container").style.display = "block"
        museum_id = data[0]["_id"]
        document.getElementsByClassName("login_error")[0].style.display = 'none'
        main()
    }
    else {
        document.getElementsByClassName("login_error")[0].style.display = 'block'
        stop_loading_animation("all_body", "block")
    }
}


/**
* A function that presents the user with the username and password update form
*/
async function display_update_password() {
    document.getElementById("id01").style.display = "block"
    document.getElementsByClassName("button_update")[0].style.display = "inline-block"
    document.getElementById("button_login").style.display = "none"
    document.getElementById("button_login").disabled = true;
    document.getElementById("old_password_label").style.display = "block"
    document.getElementById("old_password").style.display = "block"
    document.getElementById("old_password").value = ""
    document.getElementById("button_cancel").style.display = "inline-block"
    document.getElementsByClassName("login_error")[0].style.display = 'none'
    document.getElementsByClassName("user_name_password")[1].value = ""
    document.getElementsByClassName("user_name_password")[0].value = ""

}


/**
* A function that updates the new username and password in the database
*/
async function update_password() {
    //prevent default form functionalety
    event.preventDefault()
    const input_user_name_password = document.getElementsByClassName("user_name_password")
    document.getElementsByClassName("login_error")[0].style.display = 'none'
    start_loading_animation("all_body", "none")

    //Get the current username and password from the database,
    //for verification purposes, before updating them in the database
    const { data } = await DB_connention.get(`/${table_name_login}/${museum_id}`)

    //If there is no such record in the database, we get an empty array.
    if (!(Array.isArray(data))) {
        if (data.password == document.getElementById("old_password").value) {

            //Update the new username and password in the database
            DB_connention.request({
                url: `/${table_name_login}/${museum_id}`,
                method: "put",
                data: {
                    "user name": input_user_name_password[0].value,
                    password: input_user_name_password[1].value
                }

            }).then(response => {
                if (response.status != 200) {
                    show_popup_message("something went wrong please try again");

                }
                else {
                    show_popup_message("Password updated successfully");
                }

            })

            document.getElementById("id01").style.display = "none"
            stop_loading_animation("all_body", "block")
            return
        }
    }
    document.getElementsByClassName("login_error")[0].style.display = 'block'
    stop_loading_animation("all_body", "block")


}


/**
* A function that hides the password and username update form
*/
function cancel_update() {
    document.getElementById("id01").style.display = "none"
}


/**
* A function that sort a datalist element
* @param  {string} datalist_id Represents the id of the datalist element
*/
function sort_datalist(datalist_id) {
    var datalist_tag = document.getElementById(datalist_id);
    let temp_datalist = document.createElement("datalist")
    temp_datalist.innerHTML = ""
    arrTexts = new Array();
    for (i = 0; i < datalist_tag.options.length; i++) {
        arrTexts[i] = { station_name: datalist_tag.options[i].value, index: i };
    }
    arrTexts.sort((a, b) => (a.station_name > b.station_name) ? 1 : -1)
    for (i = 0; i < datalist_tag.options.length; i++) {
        temp_datalist.appendChild(datalist_tag.options[arrTexts[i].index].cloneNode(true));
    }
    datalist_tag.innerHTML = ""
    datalist_tag.innerHTML = temp_datalist.innerHTML
}

/**
* A function that sort the "current_tour_stations" table
*/
function sort_table() {
    var tbody_children = document.getElementById("current_tour_stations").children;
    arrTexts = new Array();

    for (i = 0; i < tbody_children.length; i++) {
        arrTexts[i] = {
            tr_id: tbody_children[i].id,
            station_name: tbody_children[i].children[0].textContent,
            tr_innerhtml: tbody_children[i].innerHTML
            //play_child: tbody_children[i].children[1].children[0].checked,
            //onchange_checkbox_child: tbody_children[i].children[1].children[0].attributes.onchange.nodeValue,
            //onchange_checkbox_adult: tbody_children[i].children[2].children[0].attributes.onchange.nodeValue,
            //play_adult: tbody_children[i].children[2].children[0].checked
        };
    }
    console.log(arrTexts);
    arrTexts.sort((a, b) => (a.station_name > b.station_name) ? 1 : -1)
    console.log(arrTexts);
    for (i = 0; i < tbody_children.length; i++) {
        tbody_children[i].id = arrTexts[i].tr_id;
        tbody_children[i].innerHTML = arrTexts[i].tr_innerhtml
        //tbody_children[i].children[0].textContent = arrTexts[i].station_name;
        //tbody_children[i].children[1].children[0].checked = arrTexts[i].play_child
        //tbody_children[i].children[1].children[0].attributes.onchange.nodeValue = arrTexts[i].onchange_checkbox_child
        //tbody_children[i].children[2].children[0].attributes.onchange.nodeValue = arrTexts[i].onchange_checkbox_adult
        //tbody_children[i].children[2].children[0].checked = arrTexts[i].play_adult
    }
}


/**
 * A function that displays all the stations that belong to the current tour in the table
 */
async function build_all_current_tour_stations() {
    start_loading_animation("all_body", "none")
    let current_tour_table_div_plus_btns = document.getElementById("current_tour_table_div_plus_btns")
    current_tour_table_div_plus_btns.style.display = "none"

    //Withdrawal of stations data included in the current tour from  database
    const { data } = await DB_connention.get(`/${table_name_route_info}?q={"museum_id":"${museum_id}" , "current_tour" : ${true} }
                                       &h={"$fields": {"_id": 1,"station_name": 1 , "play_child" : 1 , "play_adult" : 1 ,"current_tour" : 1} }&sort=station_name&dir=1`)

    if (data.length > 0) {
        current_tour_table_div_plus_btns.style.display = "block"
    }
    else {
        current_tour_table_div_plus_btns.style.display = "none"
    }
    //Creates an map-type variable that saves all changes made to the table of the current tour
    map_data = new Map(data.map(obj => [obj._id, obj]));
    let tbody_current_tour_stations = $("#current_tour_stations");
    tbody_current_tour_stations.empty();
    for (let i = 0; i < data.length; i++) {
        tbody_current_tour_stations.append(Create_Tr(data[i]));
    }

}


/**
* A function that builds a new record that will be added to the table in the current tour
* @param  {object} station A variable that holds the data required to build the new record
*/
function Create_Tr(station) {
    let checked_text_child = ""
    let checked_text_adult = ""
    if (station.play_child) {
        checked_text_child = "checked"
    }
    else {
        checked_text_child = ""
    }
    if (station.play_adult) {
        checked_text_adult = "checked"
    }
    else {
        checked_text_adult = ""
    }

    return `<tr id="${station._id}" class="trs_current_tour_table">
                          <td class="tds_current_tour_table border_radius_left_bottom" ><span>${station.station_name}</span></td>
                          <td class="tds_current_tour_table" ><input type="checkbox" ${checked_text_child}  onchange= "update_map('child','${station._id}')"  class="${station._id}" ></td>
                          <td class="tds_current_tour_table"><input type="checkbox" ${checked_text_adult}  onchange="update_map('adult','${station._id}')" class="${station._id}" ></td>
                          <td class="tds_current_tour_table border_radius_right_bottom">
                          <button class="w3-btn w3-ripple delete_btns" onclick="delete_station_from_current_tour('${station._id}','${station.station_name}')"><i class="fa fa-close"></i></button>
                          </td>
                        </tr>`;
}


/**
* A function that deletes a station from the table of the current tour
* @param  {string} station_id
* @param  {string} station_name
*/
function delete_station_from_current_tour(station_id, station_name) {
    let tr_tag = document.getElementById(station_id)
    let tbody_tag = document.getElementById("current_tour_stations")
    tbody_tag.deleteRow(tr_tag.rowIndex - 1)
    map_data.get(station_id).current_tour = false
    let datalist_stations_name = document.getElementById("stations_name");
    let station_name_option = document.createElement("OPTION");
    station_name_option.setAttribute("id", station_id);
    station_name_option.setAttribute("value", station_name);
    station_name_option.setAttribute("stn_name", station_name);
    datalist_stations_name.appendChild(station_name_option)
    sort_datalist("stations_name")
}


/**
* Function that updates the map variable for each change of check box in the table of the current tour
* @param  {string} child_or_adult Represents the checkbox that called the function
* @param  {string} station_id
*/
function update_map(child_or_adult, station_id) {
    if (child_or_adult == "child") {
        map_data.get(station_id).play_child = (!map_data.get(station_id).play_child)
    }
    else if (child_or_adult == "adult") {
        map_data.get(station_id).play_adult = (!map_data.get(station_id).play_adult)
    }
}


/**
 * A function that adds a new record to the table of the current tour
 */
function add_station_to_current_tour() {

    let station_name_input = document.getElementById("station_name_input")
    let station_name_input_value = station_name_input.value;
    let station_option = document.querySelector('option[stn_name="' + station_name_input_value + '"]')

    if (station_name_input_value == "" || station_option == null) {
        show_popup_message("you must choose a station from the list!")
        return
    }
    let stations_name_datalist = document.getElementById("stations_name")
    let add_station_to_current_tour_data = document.getElementsByClassName("add_station_to_current_tour_data")
    let tbody_current_tour_stations = $("#current_tour_stations");

    let station_object = {
        station_name: station_name_input_value,
        _id: station_option.id,
        play_child: add_station_to_current_tour_data[0].checked,
        play_adult: add_station_to_current_tour_data[1].checked,
        current_tour: true
    }
    tbody_current_tour_stations.append(Create_Tr(station_object))
    map_data.set(station_object._id, station_object)
    station_name_input.value = ""
    add_station_to_current_tour_data[0].checked = ""
    add_station_to_current_tour_data[1].checked = ""
    stations_name_datalist.removeChild(station_option)
    sort_table()
    current_tour_table_div_plus_btns.style.display = "block"
}


/**
 * A function that pulls from the database all the station names by specified museum_id and not in current tour,
 * initializes the variable datalist_stations_name with those names.
 */
async function build_all_stations_not_in_current_tour() {
    const { data } = await DB_connention.get(`/${table_name_route_info}?q={"museum_id":"${museum_id}" , "current_tour" : ${false} }
                                                                                                                                &h={"$fields": {"_id": 1,"station_name": 1 } }&sort=station_name&dir=1`)
    let datalist_stations_name = document.getElementById("stations_name");
    datalist_stations_name.innerHTML = ""

    for (i = 0; i < data.length; i++) {

        let station_name = document.createElement("OPTION");
        station_name.setAttribute("id", data[i]._id);
        station_name.setAttribute("value", data[i].station_name);
        station_name.setAttribute("stn_name", data[i].station_name);
        datalist_stations_name.appendChild(station_name)
    }

}


/**
 * A function that updates the database according to the data of the map object
 */
async function update_current_tour_stations_in_db() {
    let have_error = false
    let flag = false
    let message = "current tour updated successfully"

    for (const [key, value] of map_data.entries()) {
        if (value.current_tour == true) {
            if (!(value.play_child || value.play_adult)) {
                show_popup_message("every station in current tour must contain atleast one type of conntent to be played ")
                return
            }
        }
    }

    start_loading_animation("block_user_clicks", "block")
    console.log(map_data.entries());
    for (const [key, value] of map_data.entries()) {
        if (value.current_tour == true) {
            flag = true
        }

        await DB_connention.request({
            url: table_name_route_info + "/" + key,
            method: "put",
            data: {
                station_name: value.station_name,
                play_adult: value.play_adult,
                play_child: value.play_child,
                current_tour: value.current_tour
            }
        }).then(response => {
            if (response.status == 200) {
                if (value.current_tour == false) {
                    map_data.delete(key)
                }

            }
            else {
                have_error = true
                message = "something went wrong please try again"
            }
        });
        if (have_error) {
            show_popup_message(message);
            break;
        }
    }
    if (flag == false) {
        let current_tour_table_div_plus_btns = document.getElementById("current_tour_table_div_plus_btns")
        current_tour_table_div_plus_btns.style.display = "none"
    }
    console.log(map_data.entries());
    show_popup_message(message);
    stop_loading_animation("block_user_clicks", "none")
}


/**
 * A function that deletes all station from the table of the current tour
 */
function delete_all_station_from_current_tour() {
    let tbody_tag = document.getElementById("current_tour_stations")
    var tbody_stations_tr = document.querySelectorAll('#current_tour_stations tr');
    let datalist_stations_name = document.getElementById("stations_name");
    for (i = 0; i < tbody_stations_tr.length; ++i) {
        map_data.get(tbody_stations_tr[i].id).current_tour = false
        let station_name_option = document.createElement("OPTION");
        station_name_option.setAttribute("id", tbody_stations_tr[i].id);
        station_name_option.setAttribute("value", map_data.get(tbody_stations_tr[i].id).station_name);
        station_name_option.setAttribute("stn_name", map_data.get(tbody_stations_tr[i].id).station_name);
        datalist_stations_name.appendChild(station_name_option)
    }
    tbody_tag.innerHTML = ""
    sort_datalist("stations_name")
}


/**
 * A function that takes the user to the home page where he can view and edit all the stations data
 */
function show_station_information() {
    start_loading_animation("all_body", "none")
    document.getElementById("div_display_current_station").style.display = "none"
    document.getElementById("container").style.display = "block"
    document.getElementById("btn_home_page").style.display = "none"
    document.getElementById("btn_current_tour").style.display = "inline"
    main()

}


/**
 * A function that takes the user to the current tour page where he can view and edit the current tour data
 */
async function show_current_tour() {
    document.getElementById("container").style.display = "none"
    document.getElementById("div_display_current_station").style.display = "block"
    document.getElementById("btn_current_tour").style.display = "none"
    document.getElementById("btn_home_page").style.display = "inline"
    document.getElementById("station_content").style.display = "none"
    last_selected_station = ""
    build_all_current_tour_stations()
    await build_all_stations_not_in_current_tour()
    stop_loading_animation("all_body", "block")

}


/**
 * A function that opens for the user, the Add station current tour box
 */
function open_add_station_form() {
    document.getElementById("div_add_station_to_current_tour_table").style.display = "block"
    document.getElementById("open_add_station_form").style.display = "none"
    document.getElementById("close_add_station_form").style.display = "inline"

}


/**
 * A function that closes for the user, the Add station current tour box
 */
function close_add_station_form() {
    document.getElementById("div_add_station_to_current_tour_table").style.display = "none"
    document.getElementById("open_add_station_form").style.display = "inline"
    document.getElementById("close_add_station_form").style.display = "none"
}


/**
 * A function that displays the loading animation
 * @param  {string} element_id Represents the div we want to hide / show
 * @param  {string} visibility Whether to hide or show the div
 */
function start_loading_animation(element_id, visibility) {

    $(".loading_elements").addClass("loading__letter");
    //all_body , none || block_user_clicks ,block
    document.getElementById(element_id).style.display = visibility
    document.getElementById("animation_div").style.display = "block"

}


/**
 * A function that hides the loading animation
 * @param  {string} element_id Represents the div we want to hide / show
 * @param  {string} visibility Whether to hide or show the div
 */
function stop_loading_animation(element_id, visibility) {
    $(".loading_elements").removeClass("loading__letter");
    document.getElementById(element_id).style.display = visibility
    document.getElementById("animation_div").style.display = "none"

}


/**
 * A function that displays a message on the screen
 * @param  {string} message message content
 */
function show_popup_message(message) {
    let popup_message_content = document.getElementById("popup_message_content")
    popup_message_content.textContent = message
    let popup_message_div = document.getElementById('popup_message_div');
    popup_message_div.style.display = "block";


}


/**
 * A function that hides the displayed message from the screen
 */
function hide_popup_message() {
    let popup_message_div = document.getElementById('popup_message_div');
    popup_message_div.style.display = "none";
}


//Used to hide the message displayed on the screen when clicking on a part of the screen that is not the message itself
window.onclick = function (event) {
    let popup_message_div = document.getElementById('popup_message_div');
    if (event.target == popup_message_div) {
        popup_message_div.style.display = "none";
    }
}