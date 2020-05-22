module.exports = {
    "extends": [ "standard", "standard-react" ],
    "globals": {
      "React": true
    },
    "plugins": [
      "react",
      "jest"
    ],
    "env": {
      "browser": true
    },
    "overrides": [
      {
        "files": [
          "**/*.test.js",
          "**/*.test.jsx"
        ],
        "env": {
          "jest": true
        }
      }
    ],
    "rules": {
      "react/jsx-filename-extension": [
        1,
        {
          "extensions": [".js", ".jsx"]
        }
      ],
      "react/prop-types": [ 1 ],
      "react/jsx-uses-react": "error",
      "jest/no-identical-title": "error",
      "jest/prefer-to-have-length": "warn",
      "jest/valid-expect": "error"
    },

};
