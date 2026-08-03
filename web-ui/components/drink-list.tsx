import MuiLink from "@mui/material/Link";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { Drink } from "@/api";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";
import { formatDateTime } from "@/lib/format";

export interface DrinkListProps {
  drinks: Drink[];
  /** Hide the keg column (e.g. on a keg page). */
  hideKeg?: boolean;
  /** Hide the user column (e.g. on a drinker page). */
  hideUser?: boolean;
}

/** Tabular list of drinks with links to their detail pages. */
export function DrinkList({ drinks, hideKeg, hideUser }: DrinkListProps) {
  const { volume } = useFormatters();
  if (drinks.length === 0) {
    return <Typography color="text.secondary">No drinks yet.</Typography>;
  }
  return (
    <TableContainer sx={{ overflowX: "auto" }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Time</TableCell>
            {!hideUser && <TableCell>Drinker</TableCell>}
            <TableCell align="right">Volume</TableCell>
            {!hideKeg && <TableCell>Keg</TableCell>}
            <TableCell>Shout</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {drinks.map((drink) => (
            <TableRow key={drink.id} hover>
              <TableCell>
                <MuiLink component={Link} to={`/drinks/${drink.id}`} underline="hover">
                  {formatDateTime(drink.time)}
                </MuiLink>
              </TableCell>
              {!hideUser && (
                <TableCell>
                  <UserLink user={drink.user} />
                </TableCell>
              )}
              <TableCell align="right">{volume(drink.volume_ml)}</TableCell>
              {!hideKeg && (
                <TableCell>
                  <MuiLink component={Link} to={`/kegs/${drink.keg.id}`} underline="hover">
                    {drink.keg.beverage.name}
                  </MuiLink>
                </TableCell>
              )}
              <TableCell>{drink.shout}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
