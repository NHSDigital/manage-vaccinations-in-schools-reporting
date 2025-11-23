export default {
  testEnvironment: "jsdom",
  transform: {},
  moduleNameMapper: {
    "^(\\.{1,2}/.*)\\.js$": "$1",
  },
  testMatch: ["**/tests/javascript/**/*.test.js"],
  collectCoverage: true,
  collectCoverageFrom: [
    "mavis/reporting/javascript/**/*.js",
    "!mavis/reporting/javascript/app.js",
  ],
};

