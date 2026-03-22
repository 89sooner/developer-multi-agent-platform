import { NavLink } from "react-router-dom";

const items = [
  { to: "/workflows/new", label: "New Workflow" },
  { to: "/health", label: "Health" }
];

export function PrimaryNav({ mobile = false }: { mobile?: boolean }) {
  return (
    <nav className={mobile ? "primary-nav primary-nav-mobile" : "primary-nav"} aria-label="Primary navigation">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => (isActive ? "nav-link nav-link-active" : "nav-link")}
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
