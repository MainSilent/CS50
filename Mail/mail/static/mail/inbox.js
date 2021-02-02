document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(email) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = email ? email.sender : ''
  document.querySelector('#compose-subject').value = email ? `${email.subject.startsWith('Re:') ? '' : 'Re:'} ${email.subject}` : ''
  document.querySelector('#compose-body').value = email ? `On ${email.timestamp} ${email.sender} wrote: ${email.body}` : ''
}

function load_mailbox(mailbox) {
  document.querySelector('#emails-view').innerHTML = ''

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch('/emails/'+mailbox)
    .then(response => response.json())
    .then(emails => {
      emails.forEach(email => {
        emailElem = `
          <div class="email ${email.read ? 'read' : ''}" onclick="show_email(${email.id}, '${mailbox}')">
            <p>${email.sender}</p>
            <p>${email.subject}</p>
            <p>${email.timestamp}</p>
          </div>
        `
        document.querySelector('#emails-view').innerHTML += emailElem 
      })
    });
}

function send_email(e) {
  e.preventDefault();
  console.log(e);
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients:  document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(() => load_mailbox('sent'))
}

function show_email(id, mailbox) {
  const view  = document.querySelector('#emails-view')
  view.innerHTML = ''

  fetch('/emails/'+id, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
  .then(_ => {
    fetch('/emails/'+id)
      .then(response => response.json())
      .then(email => {
          view.innerHTML += `
            <div class="email-container">
              <p>Sender: ${email.sender}</p>
              <p>Recipients: ${email.recipients.map(e => e)}</p>
              <p>Subject: ${email.subject}</p>
              <p>Timestamp: ${email.timestamp}</p>
              <p>Body: ${email.body}</p>
            </div>
            <br/>
            ${mailbox != "sent" ? `
              <span class="archive-btn reply-btn" onclick="reply(${email.id})">Reply</span>
              <span class="archive-btn" onclick="archive(${id}, ${!email.archived})">${email.archived ? "Unarchive" : "Archive"}</span>
              ` : '' }
            `
      })
  })
}

function archive(id, status) {
  fetch('/emails/'+id, {
    method: 'PUT',
    body: JSON.stringify({ archived: status })
  })
  .then(() => load_mailbox('inbox'))
}

function reply(id) {
  fetch('/emails/'+id)
    .then(response => response.json())
    .then(email => compose_email(email))
}