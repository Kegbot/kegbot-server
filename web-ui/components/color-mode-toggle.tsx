import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import IconButton from "@mui/material/IconButton";
import { useColorScheme } from "@mui/material/styles";
import Tooltip from "@mui/material/Tooltip";

/** Light/dark switch. Follows the system until the user picks a side. */
export function ColorModeToggle() {
  const { mode, systemMode, setMode } = useColorScheme();
  const resolved = (mode === "system" ? systemMode : mode) ?? "light";
  const next = resolved === "dark" ? "light" : "dark";

  return (
    <Tooltip title={`Switch to ${next} mode`}>
      <IconButton
        color="inherit"
        onClick={() => setMode(next)}
        aria-label={`Switch to ${next} mode`}
      >
        {resolved === "dark" ? (
          <LightModeOutlinedIcon fontSize="small" />
        ) : (
          <DarkModeOutlinedIcon fontSize="small" />
        )}
      </IconButton>
    </Tooltip>
  );
}
