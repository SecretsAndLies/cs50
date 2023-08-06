document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function markEmailAsRead(email_id) {
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true,
    }),
  });
}

function changeArchiveStatus(email_id, status) {
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: status,
    }),
  }).then(() => {
    load_mailbox("inbox");
  });
}

function replyToEmail(email) {
  if (email.subject.startsWith("Re: ")) {
    subject = email.subject;
  } else {
    subject = `Re: ${email.subject}`;
  }
  console.log(email.sender);

  compose_email(
    "",
    email.sender,
    subject,
    (body = `On ${email.timestamp} ${email.sender} wrote: \n${email.body}`)
  );
}

function load_email(email_id) {
  // Show the mail and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#email-view").style.display = "block";

  fetch(`emails/${email_id}`)
    .then((response) => response.json())
    .then((email) => {
      const email_view = document.querySelector("#email-view");

      // wipe the existing html to avoid doubling up.
      email_view.innerHTML = "";

      email_view.append(createDiv(email.sender, "recipients-sender"));
      email_view.append(createDiv(email.recipients, "body-subject"));
      email_view.append(createDiv(email.subject, "email-subject"));
      email_view.append(createDiv(email.timestamp, "recipients-timestamp"));
      email_view.append(createDiv(email.body, "recipients-subject"));

      const archiveButton = document.createElement("button");
      archiveButton.classList.add("archive-button");
      email_view.append(archiveButton);

      const replyButton = document.createElement("button");
      replyButton.classList.add("reply-button");
      replyButton.innerHTML = "Reply";
      email_view.append(replyButton);
      replyButton.addEventListener("click", () => replyToEmail(email));

      markEmailAsRead(email_id);

      if (email.archived) {
        archiveButton.innerHTML = "move email to inbox";

        archiveButton.addEventListener("click", () =>
          changeArchiveStatus(email_id, false)
        );
      } else {
        archiveButton.innerHTML = "archive email";
        archiveButton.addEventListener("click", () =>
          changeArchiveStatus(email_id, true)
        );
      }
    });
}

function createDiv(content, className) {
  const element = document.createElement("div");
  element.classList.add(className);
  element.innerHTML = content;
  return element;
}

function compose_email(
  pointer = "",
  uRecipients = "",
  uSubject = "",
  uBody = ""
) {
  // HACK: for some reason, the uRecipients was being overwitten with a mouse pointer object, so I
  // replaced with a defualt and seems to work. Not ideal.
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  body = document.querySelector("#compose-body");
  subject = document.querySelector("#compose-subject");
  recipients = document.querySelector("#compose-recipients");

  document.querySelector("form").onsubmit = function () {
    fetch("/emails", {
      method: "POST",
      body: JSON.stringify({
        recipients: recipients.value,
        subject: subject.value,
        body: body.value,
      }),
    })
      .then((response) => response.json())
      .then((result) => {
        // Print result
        console.log(result);
        load_mailbox("sent");
      })
      .catch((error) => {
        console.log("Error:", error);
      });
    // Prevent default submission
    return false;
  };

  console.log("recipiants:");
  console.log(uRecipients);
  // set composition fields to user specified values (default is blank)
  recipients.value = uRecipients;
  subject.value = uSubject;
  body.value = uBody;
}

function load_mailbox(mailbox) {
  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((emails) => {
      if (emails) {
        const emails_view = document.querySelector("#emails-view");

        emails.forEach((email) => {
          let emailDiv = document.createElement("div");
          emailDiv.classList.add("email");
          emailDiv.addEventListener("click", function () {
            load_email(email.id);
          });
          emails_view.appendChild(emailDiv);

          // If the email is unread, it should appear with a white background. If the email has been read, it should appear with a gray background.

          if (!email.read) {
            emailDiv.style.background = "white";
          } else {
            emailDiv.style.background = "LightGray";
          }

          emailDiv.append(createDiv(email.subject, "email-subject"));

          emailDiv.append(createDiv(email.sender, "email-sender"));

          emailDiv.append(createDiv(email.timestamp, "email-timestamp"));
        });
      }
    });

  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#email-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;
}
