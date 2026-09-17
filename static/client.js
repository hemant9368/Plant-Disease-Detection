document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('#analysis-form');
  if (!form) return;

  const input = document.querySelector('#imagefile');
  const dropZone = document.querySelector('#drop-zone');
  const preview = document.querySelector('#preview');
  const content = document.querySelector('#drop-content');
  const fileName = document.querySelector('#file-name');
  const button = document.querySelector('#analyze-button');
  const message = document.querySelector('#form-message');
  let selectedFile;

  const showFile = (file) => {
    if (!file) return;
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      message.textContent = 'Please choose a JPG or PNG image.';
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      message.textContent = 'Please choose an image smaller than 8 MB.';
      return;
    }
    selectedFile = file;
    message.textContent = '';
    fileName.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(1)} MB`;
    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
    content.hidden = true;
    dropZone.classList.add('has-file');
  };

  input.addEventListener('change', () => showFile(input.files[0]));
  ['dragenter', 'dragover'].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add('dragging');
  }));
  ['dragleave', 'drop'].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove('dragging');
  }));
  dropZone.addEventListener('drop', (event) => showFile(event.dataTransfer.files[0]));

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      message.textContent = 'Choose a leaf image to begin.';
      input.focus();
      return;
    }
    button.disabled = true;
    button.querySelector('.button-label').textContent = 'Analysing…';
    message.textContent = '';
    try {
      const body = new FormData();
      body.append('file', selectedFile);
      const response = await fetch(form.action, { method: 'POST', body });
      const responseText = await response.text();
      let result;
      try {
        result = JSON.parse(responseText);
      } catch (_parseError) {
        throw new Error(
          response.ok
            ? 'The server returned an unexpected response. Check the deployment logs.'
            : `The upload service returned HTTP ${response.status}. Check the deployment logs.`
        );
      }
      if (!response.ok) throw new Error(result.error || 'Analysis failed.');
      window.location.assign(result.result_url);
    } catch (error) {
      message.textContent = error.message || 'Network error. Please try again.';
      button.disabled = false;
      button.querySelector('.button-label').textContent = 'Analyse leaf';
    }
  });
});
