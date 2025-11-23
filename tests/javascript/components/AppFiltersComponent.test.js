import { describe, it, expect, beforeEach, afterEach } from "@jest/globals";

import { AppFiltersComponent } from "../../../mavis/reporting/javascript/components/AppFiltersComponent.js";

describe("AppFiltersComponent", () => {
  let formElement;
  let component;

  function createForm(selectedProgramme = "flu") {
    const form = document.createElement("form");
    form.setAttribute("data-module", "app-filters");

    const programmeFieldset = document.createElement("fieldset");
    ["flu", "hpv", "menacwy", "td_ipv"].forEach((value) => {
      const label = document.createElement("label");
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "programme";
      radio.value = value;
      if (value === selectedProgramme) {
        radio.checked = true;
      }
      label.appendChild(radio);
      label.appendChild(document.createTextNode(value));
      programmeFieldset.appendChild(label);
    });
    form.appendChild(programmeFieldset);

    // Create year group checkboxes (0-13)
    const yearGroupFieldset = document.createElement("fieldset");
    yearGroupFieldset.className = "filter filter--year-group";
    for (let i = 0; i <= 13; i++) {
      const label = document.createElement("label");
      label.className = "nhsuk-checkboxes__item";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.name = "year-group";
      checkbox.value = i.toString();
      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(`Year ${i}`));
      yearGroupFieldset.appendChild(label);
    }
    form.appendChild(yearGroupFieldset);

    document.body.appendChild(form);
    return form;
  }

  function createEvent(programme, yearGroups) {
    return {
      detail: {
        parameters: {
          programme: programme,
          "year-group": yearGroups,
        },
      },
    };
  }

  beforeEach(() => {
    document.body.innerHTML = "";
    document.body.classList.add("nhsuk-frontend-supported");
  });

  afterEach(() => {
    if (formElement && formElement.parentNode) {
      formElement.parentNode.removeChild(formElement);
    }
  });

  describe("initialisation", () => {
    it("should hide invalid year groups based on initial programme selection", () => {
      formElement = createForm("hpv");
      component = new AppFiltersComponent(formElement);

      // HPV should only show year groups 8-13
      component.yearGroupCheckboxElements.forEach((checkbox) => {
        const parent = checkbox.parentElement;
        const value = parseInt(checkbox.value);
        if (value >= 8 && value <= 13) {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            false
          );
        } else {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            true
          );
        }
      });
    });
  });

  describe("hideYearGroupCheckboxes", () => {
    beforeEach(() => {
      formElement = createForm("flu");
      component = new AppFiltersComponent(formElement);
    });

    it("should show all year groups (0-13) for flu programme", () => {
      component.hideYearGroupCheckboxes("flu");

      component.yearGroupCheckboxElements.forEach((checkbox) => {
        const parent = checkbox.parentElement;
        expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
          false
        );
      });
    });

    it("should show only year groups 8-13 for hpv programme", () => {
      const hpvRadio = formElement.querySelector('input[name="programme"][value="hpv"]');
      hpvRadio.click();

      component.yearGroupCheckboxElements.forEach((checkbox) => {
        const parent = checkbox.parentElement;
        const value = parseInt(checkbox.value);
        if (value >= 8 && value <= 13) {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            false
          );
        } else {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            true
          );
        }
      });
    });

    it("should show only year groups 9-13 for menacwy programme", () => {
      const menacwyRadio = formElement.querySelector('input[name="programme"][value="menacwy"]');
      menacwyRadio.click();

      component.yearGroupCheckboxElements.forEach((checkbox) => {
        const parent = checkbox.parentElement;
        const value = parseInt(checkbox.value);
        if (value >= 9 && value <= 13) {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            false
          );
        } else {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            true
          );
        }
      });
    });

    it("should show only year groups 9-13 for td_ipv programme", () => {
      const td_ipvRadio = formElement.querySelector('input[name="programme"][value="td_ipv"]');
      td_ipvRadio.click();

      component.yearGroupCheckboxElements.forEach((checkbox) => {
        const parent = checkbox.parentElement;
        const value = parseInt(checkbox.value);
        if (value >= 9 && value <= 13) {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            false
          );
        } else {
          expect(parent.classList.contains("nhsuk-checkboxes__item--hidden")).toBe(
            true
          );
        }
      });
    });

    it("should uncheck hidden year group checkboxes", () => {
      const fluRadio = formElement.querySelector('input[name="programme"][value="flu"]');
      fluRadio.click();

      component.yearGroupCheckboxElements[0].checked = true; // Year 0
      component.yearGroupCheckboxElements[5].checked = true; // Year 5

      // Switch to HPV which hides years 0-7
      const hpvRadio = formElement.querySelector('input[name="programme"][value="hpv"]');
      hpvRadio.click();

      expect(component.yearGroupCheckboxElements[0].checked).toBe(false);
      expect(component.yearGroupCheckboxElements[5].checked).toBe(false);
    });

    it("should not uncheck visible year group checkboxes", () => {
      const hpvRadio = formElement.querySelector('input[name="programme"][value="hpv"]');
      const fluRadio = formElement.querySelector('input[name="programme"][value="flu"]');

      hpvRadio.click();

      const year8Checkbox = Array.from(
        component.yearGroupCheckboxElements
      ).find((checkbox) => checkbox.value === "8");
      year8Checkbox.checked = true;

      fluRadio.click();
      hpvRadio.click();

      expect(year8Checkbox.checked).toBe(true);
    });
  });

  describe("validateYearGroupParams", () => {
    beforeEach(() => {
      formElement = createForm("flu");
      component = new AppFiltersComponent(formElement);
    });

    it("should filter out invalid year groups for flu programme", () => {
      const event = createEvent("flu", ["0", "1", "99", "8"]);
      component.validateYearGroupParams(event);
      expect(event.detail.parameters["year-group"]).toEqual(["0", "1", "8"]);
    });

    it("should filter out invalid year groups for hpv programme", () => {
      const event = createEvent("hpv", ["0", "1", "8", "9", "13"]);
      component.validateYearGroupParams(event);
      expect(event.detail.parameters["year-group"]).toEqual(["8", "9", "13"]);
    });

    it("should filter out invalid year groups for menacwy programme", () => {
      const event = createEvent("menacwy", ["8", "9", "10"]);
      component.validateYearGroupParams(event);
      expect(event.detail.parameters["year-group"]).toEqual(["9", "10"]);
    });

    it("should filter out invalid year groups for td_ipv programme", () => {
      const event = createEvent("td_ipv", ["7", "9", "10"]);
      component.validateYearGroupParams(event);
      expect(event.detail.parameters["year-group"]).toEqual(["9", "10"]);
    });

    it("should handle single year-group value", () => {
      const event = createEvent("hpv", "8");
      component.validateYearGroupParams(event);
      expect(event.detail.parameters["year-group"]).toBe("8");
    });

    it("should delete year-group parameter when all values are invalid", () => {
      const event = createEvent("hpv", ["0", "1", "2"]);
      component.validateYearGroupParams(event);
      expect("year-group" in event.detail.parameters).toBe(false);
    });

    it("should throw error when programme is not specified", () => {
      const event = createEvent(null, ["8", "9"]);

      expect(() => {
        component.validateYearGroupParams(event);
      }).toThrow("Unexpected error: no vaccination programme specified in request parameters");
    });
  });
});

