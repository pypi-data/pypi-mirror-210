import React, { ReactElement } from "react";
export interface ITabOption {
    label: string | ReactElement;
    key: string;
    disabled?: boolean;
}
interface DefaultProps {
    tabs: ITabOption[];
    selectedKey: string;
    onSelected: (selectedKey: string, index: number) => void;
    allowEdit?: boolean;
    onEditLabel?: (label: string, index: number) => void;
}
export default function Default(props: DefaultProps): React.JSX.Element;
export {};
