import { Action } from "../types/action";
import { Labels } from "../types/labels";

export const formatActionJson = (action: Action) => { 
    // Make the label items json
    if (action.descriptions) {
        action.descriptions.forEach(desc => {
            if (desc.labels) {
                desc.labels = desc.labels.map(label => ({
                    ...label,
                    json: JSON.stringify(label.json)
                }));
            }
        });
    }
    return action;
}

export const parseLabels = (labels: Labels[]) => {
    return labels.map((label: any) => ({
        ...label,
        json: JSON.parse(label.json)
    }));
}

export const deformatActionJson = (action: Action) => {
    // Make the label items json
    if (action.descriptions) {
        action.descriptions.forEach(desc => {
            if (desc.labels) {
                desc.labels = desc.labels.map(label => ({
                    ...label,
                    json: JSON.parse(label.json)
                }));
            }
        });
    }
    return action;
}