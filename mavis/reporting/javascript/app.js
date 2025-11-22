import "htmx.org";
import { createAll, Header } from "nhsuk-frontend";

import { AppFiltersComponent } from "./components/AppFiltersComponent";

document.addEventListener("DOMContentLoaded", () => {
  createAll(Header);
  createAll(AppFiltersComponent);
});

document.addEventListener("htmx:afterRequest", (event) => {
  const url = new URL(event.detail.xhr.responseURL);
  // If the htmx request has been redirected to the start page,
  // redirect the user to the start page
  if (url.pathname == "/start") {
    window.location.href = url.toString();
  }
});
