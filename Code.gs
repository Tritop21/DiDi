var i = 0;
const suggestions = [];
const sentences = [];

function onOpen(e) {
  DocumentApp.getUi().createAddonMenu()
      .addItem('Activate Di Di', 'addSideBar')
      .addToUi();
}

function onInstall(e) {
  onOpen(e);
}

function addSideBar(){
  var htmlOutput = HtmlService.createHtmlOutputFromFile('Sidebar')
      .setTitle('Di Di')
      .setWidth(500);
  DocumentApp.getUi().showSidebar(htmlOutput);
}

function callFlaskAPI() {
  var apiUrl = 'https://d4be-103-145-154-250.ngrok-free.app/checkid/' + "1XU4yBtiBIonSsxa4FO6uN_mo_NZbPsEx36Wk2HMiq2U/1I66eo7dhGk_kcYNaDanTlPhJfl2vtFkuIaAd_iqIH8M";

  var headers = {
    "ngrok-skip-browser-warning": "any_value"
  };
  
  var options = {
    "method" : "get",
    "headers" : headers
  };
  
  var response = UrlFetchApp.fetch(apiUrl, options);
  Logger.log(response.getContentText());
  
  var jsonResponse = JSON.parse(response.getContentText());
  Logger.log(jsonResponse);

  var properties = PropertiesService.getScriptProperties();
  properties.setProperty('Sentence1', jsonResponse["Sentence1"]);
  properties.setProperty('Sentence2', jsonResponse["Sentence2"]);
  properties.setProperty('Suggestion1', jsonResponse["Suggestion1"]);
  properties.setProperty('Suggestion2', jsonResponse["Suggestion2"]);

  Logger.log(sentences[0]);

  dataReady = true;

  return jsonResponse;
}

function getSentence(index) {
  var properties = PropertiesService.getScriptProperties();
  var sentence = properties.getProperty('Sentence' + (index + 1));
  
  Logger.log(sentence);
  return sentence;
}

function getReason() {
  var jsonResponse = callFlaskAPI();
  var response1 = jsonResponse["Response1"];
  var response2 = jsonResponse["Response2"];
  var response3 = jsonResponse["Response3"];
  var response4 = jsonResponse["Source"];
  return response1 + "\n\n" + response2 + "\n\n" + response3 + "\n\n" + response2 + "\n\n" + "SOURCE:" + response4;
}

function getReplaceTextFromGS(index) {
  var properties = PropertiesService.getScriptProperties();
  var suggestion = properties.getProperty('Suggestion' + (index + 1));
  
  Logger.log(suggestion);
  return suggestion;
}

function getId(docId) {
  var url = 'https://b310-34-106-105-12.ngrok-free.app/api';
  var request = url + 'check/' + docId;
  
  try {
    var response = UrlFetchApp.fetch(request);
    var content = response.getContentText();
    
    Logger.log(content);
    
    var data;
    try {
      data = JSON.parse(content);
    } catch (e) {
      Logger.log('Error parsing JSON: ' + e.toString());
      return { error: 'Invalid JSON response' };
    }
    
    return data;
  } catch (e) {
    Logger.log('Error fetching URL: ' + e.toString());
    return { error: 'Failed to fetch data' };
  }
}

function getFiles() {
  var files = [];
  var driveFiles = DriveApp.getFiles();
  while (driveFiles.hasNext()) {
    var file = driveFiles.next();
    files.push(file.getName());
  }
  return files;
}

function replaceTextInDoc(findText, replaceText) {
  var body = DocumentApp.getActiveDocument().getBody();
  var searchResult = body.findText(findText);

  while (searchResult !== null) {
    var element = searchResult.getElement();
    var text = element.asText();
    var start = searchResult.getStartOffset();
    var end = searchResult.getEndOffsetInclusive();

    text.deleteText(start, end);
    text.insertText(start, replaceText);
    text.setBackgroundColor(start, start + replaceText.length - 1, '#d0f0c0');

    searchResult = body.findText(findText, searchResult);
  }
}

function highlightText(findText) {
  var body = DocumentApp.getActiveDocument().getBody();
  var searchResult = body.findText(findText);

  while (searchResult !== null) {
    var element = searchResult.getElement();
    var text = element.asText();
    var start = searchResult.getStartOffset();
    var end = searchResult.getEndOffsetInclusive();

    text.setBackgroundColor(start, end, '#FFFF00'); // Highlight with yellow color

    searchResult = body.findText(findText, searchResult);
  }
}

function unhighlightText(findText) {
  var body = DocumentApp.getActiveDocument().getBody();
  var searchResult = body.findText(findText);

  while (searchResult !== null) {
    var element = searchResult.getElement();
    var text = element.asText();
    var start = searchResult.getStartOffset();
    var end = searchResult.getEndOffsetInclusive();

    text.setBackgroundColor(start, end, null);

    searchResult = body.findText(findText, searchResult);
  }
}