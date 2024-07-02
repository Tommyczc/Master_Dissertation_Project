/**
 * get current url in local storage
 * @return {string}
 */
function getCurrentURL(){
    let url=window.localStorage.getItem("clientLastURL")
    return url;
}

/**
 * set the current url in local storage
 * @param url
 */
function setCurrentURL(url){
    window.localStorage.setItem("clientLastURL",url);
}


function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
}

