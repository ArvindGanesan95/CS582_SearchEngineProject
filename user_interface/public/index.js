$.ajaxSetup({
    headers: {
        'Content-Type': 'application/json'
    }
})

let paginationCounter = 0
let searchResultsList = []
const getResultsForQuery = () => {

    let searchQuery = $('#queryTerm').val()
    let data = {
        "searchString": searchQuery,
    }
    $.post("/processQuery", JSON.stringify(data))
    .done((data) => {
        paginationCounter = 0
        searchResultsList = []
        $('#searchResultsList').html('')
        searchResultsList = JSON.parse(data.replaceAll("'", '"'))
        processData()
    }).fail((error)=> {
        console.error(error)
    })
}

const processData = () => {
    let topResults = searchResultsList.slice(paginationCounter, paginationCounter + 10)
    let listDom = $('#searchResultsList')
    let html = ``

    topResults.forEach((data, index) => {
        html += `<li class="list-group-item">${data}</li>`
    })
    listDom.append(html)
    paginationCounter += 10
}