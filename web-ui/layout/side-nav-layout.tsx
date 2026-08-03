import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import Paper from "@mui/material/Paper";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import type { ReactNode } from "react";
import { Link, useLocation } from "react-router";

export interface SideNavItem {
  label: string;
  to: string;
}

export interface SideNavSection {
  /** Optional group header (mono-uppercase). */
  header?: string;
  items: SideNavItem[];
}

export interface SideNavLayoutProps {
  sections: SideNavSection[];
  children: ReactNode;
}

/**
 * Sectioned side navigation with content beside it (stacked on small
 * screens). Used by both the account and admin areas.
 */
export function SideNavLayout({ sections, children }: SideNavLayoutProps) {
  const location = useLocation();
  const theme = useTheme();
  const narrow = useMediaQuery(theme.breakpoints.down("md"));

  const allItems = sections.flatMap((section) => section.items);
  const active = allItems.reduce(
    (best, item) =>
      location.pathname === item.to ||
      (location.pathname.startsWith(`${item.to}/`) && item.to.length > best.length)
        ? item.to
        : best,
    allItems[0]?.to ?? "",
  );

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: narrow ? "column" : "row",
        gap: 3,
        alignItems: "flex-start",
      }}
    >
      <Paper variant="outlined" sx={{ width: narrow ? "100%" : 216, flexShrink: 0 }}>
        <List dense sx={{ py: 0.5 }}>
          {sections.map((section, index) => (
            <Box key={section.header ?? index}>
              {section.header && <ListSubheader disableSticky>{section.header}</ListSubheader>}
              {section.items.map((item) => (
                <ListItemButton
                  key={item.to}
                  component={Link}
                  to={item.to}
                  selected={active === item.to}
                  sx={{
                    borderLeft: 2,
                    borderColor: active === item.to ? "primary.main" : "transparent",
                  }}
                >
                  <ListItemText primary={item.label} />
                </ListItemButton>
              ))}
              {index < sections.length - 1 && <Divider component="li" sx={{ my: 0.5 }} />}
            </Box>
          ))}
        </List>
      </Paper>
      <Box sx={{ flexGrow: 1, width: "100%", minWidth: 0 }}>{children}</Box>
    </Box>
  );
}
