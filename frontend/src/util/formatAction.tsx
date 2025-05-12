import { Action } from "../types/action";

export const formatActionJson = (action: Action) => { 
// Make the label items json
if (action.labels) {
    action.labels = action.labels.map((label) => {
    return {
        ...label,
        json: JSON.stringify(label.json)
    };
    });
}
return action;
}