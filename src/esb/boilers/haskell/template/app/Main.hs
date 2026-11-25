{-  ElfScript Brigade
 -
 -  Advent Of Code {year} Day {day}
 -  Haskell Solution
 -
 -  {problem_title}
 -
 -  https://{problem_url} -}
module Main where

import Fireplace

solvePt1 :: String -> [String] -> Int
solvePt1 input _args = do
  pure 25

solvePt2 :: String -> [String] -> String
solvePt2 input _args = do
  pure "December"

main :: IO ()
main = do
  -- 🎅🎄❄️☃️🎁🦌
  -- Bright Christmas lights HERE
  v1Run solvePt1 solvePt2
