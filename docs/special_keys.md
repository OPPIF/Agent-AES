# Cognitive label styling

Certain key-value pairs in message tables require custom styling. The Web UI uses a `specialKeys` mapping in `webui/js/messages.js` to link specific labels to CSS classes:

```javascript
const specialKeys = {
  thoughts: "msg-thoughts",
  reasoning: "msg-thoughts",
};
```

## Adding new labels

To style additional cognitive labels:

1. Add the label and desired CSS class to the `specialKeys` object.
2. Define the CSS rules for the new class (for example in `webui/css/messages.css`).

Example:

```javascript
specialKeys.analysis = "msg-analysis";
```

This approach keeps cognitive styling centralized and easy to extend.
