import { Component } from "nhsuk-frontend";

const YEAR_GROUPS_HPV = ["8", "9", "10", "11", "12", "13"];
const YEAR_GROUPS_DOUBLES = YEAR_GROUPS_HPV.slice(1);
const YEAR_GROUPS_ALL = ["0", "1", "2", "3", "4", "5", "6", "7"].concat(YEAR_GROUPS_HPV);

const YEAR_GROUPS_BY_PROGRAMME = {
  "flu": YEAR_GROUPS_ALL,
  "hpv": YEAR_GROUPS_HPV,
  "menacwy": YEAR_GROUPS_DOUBLES,
  "td_ipv": YEAR_GROUPS_DOUBLES,
};

export class AppFiltersComponent extends Component {
  static moduleName = "app-filters";

  /**
   * @param {HTMLFormElement} element
   */
  constructor(formElement) {
    super(formElement);
    this.yearGroupCheckboxElements = formElement.querySelectorAll(".filter--year-group input[type='checkbox']");

    formElement.addEventListener("change", this.hideYearGroupCheckboxes.bind(this));
    document.addEventListener("htmx:configRequest", this.validateYearGroupParams.bind(this));
  }

  hideYearGroupCheckboxes(event) {
    if (event.target.name === "programme") {
      const programme = event.target.value;
      const validYearGroups = YEAR_GROUPS_BY_PROGRAMME[programme];

      this.yearGroupCheckboxElements.forEach((element) => {
        if (validYearGroups.includes(element.value)) {
          element.parentElement.classList.remove("nhsuk-checkboxes__item--hidden");
        } else {
          element.parentElement.classList.add("nhsuk-checkboxes__item--hidden");
          if (element.checked) {
            element.checked = false;
          }
        }
      });
    }
  }

  validateYearGroupParams(event) {
    let yearGroupParams = event.detail.parameters["year-group"];
    const programme = event.detail.parameters["programme"];
    const validYearGroups = YEAR_GROUPS_BY_PROGRAMME[programme];

    if (!yearGroupParams) return;
    if (!programme) {
      throw new Error("Unexpected error: no vaccination programme specified in request parameters");
    };

    // Convert single value to an array
    if (!Array.isArray(yearGroupParams)) {
      yearGroupParams = [yearGroupParams];
    }

    // Can't use Array.filter because we're dealing with a proxy object
    const newYearGroupParams = [];
    yearGroupParams.forEach((param) => {
      if (validYearGroups.includes(param)) {
        newYearGroupParams.push(param);
      }
    });

    if (newYearGroupParams.length === 0) {
      delete event.detail.parameters["year-group"];
      return;
    }

    // Convert back to a single value if there's only one
    if (newYearGroupParams.length > 1) {
      event.detail.parameters["year-group"] = newYearGroupParams;
    } else {
      event.detail.parameters["year-group"] = newYearGroupParams[0];
    }
  }
}
