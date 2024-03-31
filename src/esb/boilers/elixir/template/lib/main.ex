defmodule Year{year}Day{day} do
  @moduledoc """
  ElfScript Brigade

  Advent Of Code {year} Day {day}
  Elixir Solution

  {problem_title}

  https://{problem_url}
  """
  import EsbFireplace

  defp solve_pt1(input_data, _args) do
    # Solve pt1
    :hello
  end

  defp solve_pt2(input_data, _args) do
    # Solve pt2
    :world
  end

  def start do
    # 🎅🎄❄️☃️🎁🦌
    # Bright christmas lights HERE
    v1_run(&solve_pt1/2, &solve_pt2/2)
  end
end
