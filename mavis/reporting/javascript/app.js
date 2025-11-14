import { createAll, Header } from "nhsuk-frontend";
import "htmx.org";

createAll(Header);

document.addEventListener("htmx:afterRequest", (event) => {
  const url = new URL(event.detail.xhr.responseURL);
  // If the htmx request has been redirected to the start page,
  // redirect the user to the start page
  if (url.pathname == "/start") {
    window.location.href = url.toString();
  }
});
