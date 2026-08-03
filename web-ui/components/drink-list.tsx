import MuiLink from "@mui/material/Link";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Tooltip from "@mui/material/Tooltip";
import { Link } from "react-router";
import type { Drink } from "@/api-client";
import { EmptyState } from "@/components/empty-state";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";
import { formatDateTime } from "@/lib/format";
import { MONO_FONT } from "@/theme/typography";

export interface DrinkListProps {
  drinks: Drink[];
  /** Hide the keg column (e.g. on a keg page). */
  hideKeg?: boolean;
  /** Hide the user column (e.g. on a drinker page). */
  hideUser?: boolean;
}

/**
 * Tabular list of drinks. Conventions: the "poured" column is the
 * row's primary (accent) link; entity links are quiet; numerals and
 * times are mono.
 */
export function DrinkList({ drinks, hideKeg, hideUser }: DrinkListProps) {
  const { volume, compactRelative } = useFormatters();
  if (drinks.length === 0) {
    return <EmptyState title="No drinks yet." hint="Pours will show up here as they happen." />;
  }
  return (
    <TableContainer sx={{ overflowX: "auto" }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Poured</TableCell>
            {!hideUser && <TableCell>Drinker</TableCell>}
            <TableCell align="right">Volume</TableCell>
            {!hideKeg && <TableCell>Keg</TableCell>}
            <TableCell>Shout</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {drinks.map((drink) => (
            <TableRow key={drink.id} hover>
              <TableCell sx={{ fontFamily: MONO_FONT, whiteSpace: "nowrap" }}>
                <Tooltip title={formatDateTime(drink.time)} placement="top-start">
                  <MuiLink component={Link} to={`/drinks/${drink.id}`} underline="hover">
                    {compactRelative(drink.time)}
                  </MuiLink>
                </Tooltip>
              </TableCell>
              {!hideUser && (
                <TableCell>
                  <UserLink user={drink.user} muted />
                </TableCell>
              )}
              <TableCell align="right" sx={{ fontFamily: MONO_FONT, whiteSpace: "nowrap" }}>
                {volume(drink.volume_ml)}
              </TableCell>
              {!hideKeg && (
                <TableCell>
                  <MuiLink
                    component={Link}
                    to={`/kegs/${drink.keg.id}`}
                    underline="hover"
                    color="inherit"
                  >
                    {drink.keg.beverage.name}
                  </MuiLink>
                </TableCell>
              )}
              <TableCell sx={{ color: "text.secondary" }}>{drink.shout}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
