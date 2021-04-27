$.ajaxSetup({
    headers: {
        'Content-Type': 'application/json'
    }
})

let paginationCounter = 0
let searchResultsList = []
const getResultsForQuery = () => {

    let searchQuery = $('#queryTerm').val()
    if (searchQuery == "") {
        console.log("Enter a search query")
        return
    }
    let selectedRankingAlgorithm = $('input[name=inlineDefaultRadiosExample]:checked').attr('id')
    console.log(selectedRankingAlgorithm)
    if (selectedRankingAlgorithm === undefined) {
        selectedRankingAlgorithm = null
    }
    else
    selectedRankingAlgorithm = selectedRankingAlgorithm.toLowerCase()
    let data = {
        "searchString": searchQuery,
        "rankingAlgorithm": selectedRankingAlgorithm
    }
    $.post("/processQuery", JSON.stringify(data))
    .done((data) => {
        paginationCounter = 0
        searchResultsList = []
        $('#searchResultsList').html('')
        searchResultsList = JSON.parse(data.replaceAll("'", '"'))
        processData()
    }).fail((error)=> {
        console.error("Error occurred"+error)
        // Show it in hidden box
    })
}

const processData = () => {
    if(paginationCounter >= searchResultsList.length) return

    let topResults = searchResultsList.slice(paginationCounter, paginationCounter + 10)
    let listDom = $('#searchResultsList')
    let html = ``

    topResults.forEach((data, index) => {
        html += `<li class="list-group-item"><a href='${data}' target="_blank">${data}</a></li>`
    })
    listDom.append(html)
    paginationCounter += 10
}