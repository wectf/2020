// send post request, if auth == true, send the request with user token in localStorage
function post(action, params, callback, auth=false) {
    let data = new FormData();
    data.append("action", action);
    if (auth)
        data.append("user", localStorage.getItem("user"));
    for (let key in params){
        if (params.hasOwnProperty(key)){
            data.append(key, params[key])
        }
    }
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/', true);
    xhr.onload = function () {
        !callback ? console.log(this.responseText) : callback(JSON.parse(this.responseText));
    };
    xhr.send(data);
}

// login / register handler
function auth(mode="login") {
    const username = document.getElementById(`${mode}_username`).value;
    const password = document.getElementById(`${mode}_password`).value;
    post(mode, {
        username: username,
        password: password,
    }, (v)=>{
        if (v["success"] === 1){
            // enable safe mode in default
            localStorage.setItem("safe_mode", "1");
            localStorage.setItem("user", v["result"]);
            localStorage.setItem("is_auth", "1");
            window.location.href = "/home.html";
            return;
        }
        document.getElementById(`${mode}_error`).style.display = "block";
        document.getElementById(`${mode}_error_info`).innerText = v["message"];
    })
}

// add new note handler
function add_note() {
    const content = document.getElementById(`add_note_content`).value;
    post('add_note', {
        content: content,
    }, (v)=>{
        if (v["success"] === 1){
            window.location.href = "/home.html";
            return;
        }
        document.getElementById(`add_note_error`).style.display = "block";
        document.getElementById(`add_note_error_info`).innerText = v["message"];
    }, true)
}

// the function to echo the safe mode related texts
function safe_echo() {
    if (localStorage.getItem("safe_mode") === "1")
        document.write(`
        <h1>
            Safe Post
        </h1>
        <p>Hi! You can see this post because you have enabled safe mode.</p>
        <p>In safe mode, you can only view this post and add your notes (write-only).</p>
        <p>Since we have a sharing function && we hope we can protect you from all potential XSS, this is enabled in default.</p>
        <p>You can turn it off by clicking following button. Turn it off at your own risk.</p>
        <button class="ui button " onclick="turn_safe_mode('0');">Turn off safe mode</button>
    
        `);
    else
        document.write(`
        <h1>
            Safe Post
        </h1>
        <p>You are not in safe mode and in danger of potential XSS attack.</p>
        <button class="ui button " onclick="turn_safe_mode('1');">Turn on safe mode</button>
    
        `)
}

// get all user's notes
function get_user_notes() {
    if (localStorage.getItem("safe_mode") === "1")
        return;
    post("user_notes", {}, (v)=>{
        if (v["success"] === 1){
            let html = "";
            v["result"].map((obj)=>{
              html += `
                <div class="ui card" style="width: 100%; cursor: pointer" 
                    onclick="window.location.href='note.html#${obj['token']}'">
                <div class="content">
                    <p>${obj["content"]}</p>
                </div>
                </div>
              `
            });
            document.getElementById("notes").innerHTML = html;
            if (v["result"].length === 0 ) {
                document.getElementById("notes_info").style.display = "block";
                document.getElementById("notes_info_content").innerText = "You haven't make any note yet : ()"
            }
        }
    }, true);
}

// turn on / off safe mode, '1' -> enabled, '0' -> disabled
function turn_safe_mode(mode) {
    localStorage.setItem('safe_mode', mode);
    window.location.href = "/home.html";
}

function logout() {
    localStorage.setItem("is_auth", '0');
    localStorage.setItem("user", '');
    check_auth();
}

function check_auth() {
    if (localStorage.getItem("is_auth") === '0')
        window.location.href = '/';
}

function get_note(token) {
    post('get_note', {
        token: token,
    }, (v)=>{
        if (v["success"] === 1){
            document.getElementById("note_id").innerText = v["result"]["id"];
            document.getElementById("note_author").innerText = v["result"]["author_info"]["name"];
            document.getElementById("note_content").innerHTML = v["result"]["content"]
        }
    }, true)
}
