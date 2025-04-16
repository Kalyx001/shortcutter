document.getElementById('clip-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const url = document.getElementById('yt-url').value;
  const start = document.getElementById('start-time').value;
  const end = document.getElementById('end-time').value;

  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('result').innerHTML = '';

  try {
    const response = await fetch('/cut', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, start, end })
    });

    const data = await response.json();
    document.getElementById('loading').classList.add('hidden');

    if (data.link) {
      document.getElementById('result').innerHTML = `
        <p>✅ Clip ready!</p>
        <a href="${data.link}" download>Download Your Clip</a>
      `;
    } else {
      document.getElementById('result').innerHTML = `<p>❌ Error: ${data.error}</p>`;
    }
  } catch (err) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('result').innerHTML = `<p>❌ Unexpected error occurred.</p>`;
  }
});
