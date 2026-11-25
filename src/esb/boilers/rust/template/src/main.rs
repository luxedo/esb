/*
* ElfScript Brigade
*
* Advent Of Code {year} Day {day}
* Rust Solution
*
* {problem_title}
*
* https://{problem_url}
*
*/

use esb_fireplace::{FireplaceError, FireplaceResult};

use std::fmt::Display;

fn solve_pt1(input_data: &str, _args: Vec<String>) -> FireplaceResult<impl Display> {
    Ok(25)
}

fn solve_pt2(input_data: &str, _args: Vec<String>) -> FireplaceResult<impl Display> {
    Ok("December")
}

fn main() -> Result<(), FireplaceError> {
    // 🎅🎄❄️☃️🎁🦌
    // Bright Christmas lights HERE
    esb_fireplace::v1_run(solve_pt1, solve_pt2)?;
    Ok(())
}
