---
title: "Flow’s OCaml to Rust Port"
source: "https://medium.com/flow-type/flows-ocaml-to-rust-port-78b95bcf49e9"
author:
  - "[[Sam Zhou]]"
published: 2026-06-25
created: 2026-06-27
description: "Flow’s OCaml codebase has been completely ported to Rust! Since v0.319 (released on June 17, 2026), our flow-bin npm package has been powere"
tags:
  - "clippings"
---

関連: [[Patterns]]

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*7U6Z9KnvNz5u529hcswAZw.png)

Flow has been ported to Rust

Flow’s OCaml codebase has been completely ported to Rust! Since v0.319 (released on June 17, 2026), our [flow-bin npm package](https://www.npmjs.com/package/flow-bin) has been powered by the Rust binary.

We measured the performance of the new Rust-based Flow binary on huge internal JS codebases, and found it’s generally **2x faster** than the OCaml binary across most of the type-checking stages, and 30% to 100% faster in the most computationally intensive checking stage.

In this blog post, we’ll walk through the entire engineering journey of the Rust port.

## History

We first explored the idea of a Rust rewrite back in 2019, when we were facing scalability issues in our internal massive monorepos. At that time, we concluded that a rewrite would be very costly and time consuming, and our scalability would reach a breaking point before we were able to complete the rewrite. Therefore, we eventually shelved the idea, and pursued other architecture improvements like [Types-First](https://medium.com/flow-type/types-first-a-scalable-new-architecture-for-flow-3d8c7ba1d4eb).

We had not seriously revisited the Rust rewrite/port idea for years. We certainly wanted the broader Rust ecosystem support, superior Rust IDE features, and the fearless concurrency model of Rust. We would also like to avoid dealing with occasional OCaml CI breakages that are hard to debug and are release blocking. However, none of these points could justify a daunting Rust rewrite with a long time horizon and uncertain payoff.

In 2025, three major events have completely shifted the calculus. Inside Meta, we saw [Pyrefly](https://pyrefly.org/) (a Rust rewrite of Pyre from OCaml) delivering more than 30x perf improvement. External to Meta, [TypeScript announced a Go port that is 10x faster than the JS one](https://devblogs.microsoft.com/typescript/typescript-native-port/). With these events, we have seen the benefits and feasibility of such rewrites or ports. A potential Flow Rust port started to become a serious discussion topic between our team members, even though we still have not committed any time and effort into this yet. In late 2025, rapid advancement of AI showed early promise that we can significantly shorten the time span of a Rust port, especially if we stick to a line-by-line mechanical port.

## Key Decisions

Before going into the technical details, it’s worth going over all the key decisions we made and the reasoning behind them.

### Rust port, instead of Go or Kotlin port

If we simply wanted to move away from OCaml to a language with larger community and more paved-path solutions, Go or Kotlin would be safer choices. OCaml, Go, Kotlin (on JVM) all use a mark-and-sweep GC strategy, which is quite suitable for typical programming language workloads. Compared to a Rust port, porting to Go or Kotlin could save us a lot of time debugging perf regressions due to GC vs malloc differences.

However, we eventually decided on a potentially more risky Rust port, because simply moving away from OCaml was not the only goal. A successful Rust port would also open us to additional integration opportunities with a proliferation of Rust-based JS toolchain like SWC and oxlint.

In addition, no matter how good AI has become, ports are still risky and costly, so we wanted to only do it once and be very certain that we wouldn’t regret the language choice again. We believed the Rust port can offer that guarantee.

### Line-by-line port, instead of a rewrite

While rewrites are always more exciting and can give us opportunities to fix long standing issues, they are significantly more risky. We wanted the final product to be a mostly drop-in replacement with no significant change in behavior, so we decided to do a conservative and mostly line-by-line port.

We know that a line-by-line port will unfortunately copy over some bad decisions of the type checker that have accumulated over the years, but it is the only realistic path forward if we don’t want to burden ourselves with complicated rollouts.

Therefore, we decided to stick to the strict line-by-line port through the entire project and rejected AI changes that took too much liberty. The only major exception is the shared memory system, where we did a clean Rust replacement, instead of porting over the C-based shared memory workaround from the lack of multi-threading support pre-OCaml-5.

### Favor progress over fully idiomatic Rust

We could choose to carefully study the well-implemented Rust compiler to have a fully idiomatic Rust port, that will likely have even better performance compared to the approach we took, which sometimes results in just writing OCaml in Rust syntax with `RC` and `RefCell` everywhere.

However, we know that a full idiomatic Rust codebase would likely require a serious rethink and rewrite of the existing OCaml codebase first if we wanted to stick to the line-by-line port principle. This is the additional effort we cannot afford with the risk of further complicating the project. Therefore, we decided to defer all such potential improvements after the completion of Rust port: it’s always easier to do one thing at a time.

## Get Sam Zhou’s stories in your inbox

Join Medium for free to get updates from this writer.

We still did not favor progress at all costs. We did enforce a strict no-unsafe rule for AI (a few unsafe blocks we have are intentional and written by humans).

## A heavily AI-assisted Rust port

### The parser port

The AI assisted Rust port started quite unambitiously: all we hoped was that the AI can migrate the codebase function by function. Given the mechanical nature of the line-by-line port, AI is probably less likely to make dumb mistakes than humans, such as accidentally missing a token consumption line during parsing.

In addition, even weaker AI models can provide some baseline intelligence in an automated way, so that it can make some local smart decisions to avoid a completely mechanical but ugly port. For example, in OCaml, values are prepended to lists like `foo :: my_list`, while in Rust we should just use vectors. At the time we were doing the parser port, the most powerful model was Sonnet 4.5 and it could make these decisions accurately most of the time.

At the time of the parser port in late 2025, AI could still port at most several functions at a time before having serious performance breakdowns, so we were still manually running prompts like “port function A, B and C”, manually reviewing them, and then asking it to continue to port a few more and so on.

Even in this slower setting, the author of the post was able to port the entire parser alone, with all tests passing and 2x perf improvement in 4 weeks. The promising pace and early perf numbers helped secure the “go” decision for the entire Rust port project.

### The checker port

Once the parser port was done, we spent a month porting over various smaller systems that are necessary to power the actual checker, such as module resolution, dependency analysis, and type signature extraction. Then we moved on to the type checker port.

During the checker port, the state of the art AI model was Opus 4.5/4.6, which could run much larger porting workload autonomously for a long period of time. We noticed the significant capability improvement and took advantage of it. Using agent teams, we were able to port the entire type checker in a month, which was considerably more complicated than the parser.

We were cautious with the claim of [creating a c-compiler with AI alone](https://www.anthropic.com/engineering/building-c-compiler), so we still spent time to enforce our decision of line-by-line port rigorously. We used a combination of different techniques:

- Agent teams where reviewer agents checked against [claude.md](http://claude.md/) guidelines and rejected bad changes.
- Instructions to ask AI to include original OCaml code as comments side by side with the ported Rust code, so that non-line-by-line port had nowhere to hide (those comments were later deleted as humans manually review the code).
- A final round of human review to ensure that AI didn’t come up with weird ways or excuses to workaround these restrictions.

In early March, we finally had a code-complete full-check pipeline. Unsurprisingly, when we first tried to run it, zero checker tests were successful. Nevertheless, we made it pass all checker tests with continuous AI run in a week. During the week, one day it bumped the test passing rate from 20% to 60% in just one full night run. This was the time when the strict line-by-line port rule really paid off. AI agents can make local reasoning to find the defects in earlier ports, and human reviewers can make local decisions on whether the AI fixes stick to the guidelines and whether they fix real problems.

### No code freeze

Once the checker port was complete, we added CI jobs to ensure that the same integration tests the OCaml code needed to pass must also pass with the Rust implementation. In the past, such measures would need to be accompanied with a code freeze of the OCaml code, because it would be too much effort to simultaneously advance both codebases at the same time in an identical way. However, with AI agents, it was almost as easy as an additional “port this to rust” prompt. Such ports are way easier than the initial port, since at this time the foundation has already been figured out and AI agents only need to follow existing examples. The rest of the team continued to ship features this way throughout the Rust port period.

### Performance optimizations

When the checker port was complete, we were able to finish the port of the rest of the system quite quickly in a month. However, we still had the challenge that the Rust port at the time significantly under-performed the OCaml one.

AI agents were able to quickly identify and fix many obvious big-O related issues. After it resolved all the easy issues, it was still OOMing in some large Flow roots. We speculated that there might be a memory leak, so we directed the agents to identify them, and they came back with a fix that manually breaks cycles due to `RC` and `RefCell`.

Later, we asked AI agents to use profiling tools to measure hot spots and optimize accordingly. This was a perfect use case for a Ralph-loop, where the goal is clear and the potential to improve performance seems endless. AI was able to continuously find 1% and 2% improvements that are likely to be considered noise and discarded by humans who don’t have enough time to verify these potential micro-optimizations, but these optimizations do add up over time.

Finally, we still need to acknowledge that AI won’t solve all perf issues on its own. In several instances, AI has spent days finding nothing worth optimizing, where we used our insights to find large opportunities of optimization (work-stealing scheduler) or large defects in port (implicitly repeated computations).

## Final remarks

We are happy that we are able to ship this ambitious Rust port to all of our users, establish a more solid foundation of future development, and share the engineering story to the world.

Especially in this year, we have seen several major ports being completed. In the spectrum from attention to detail to fully autonomous porting, our Rust port is likely similar to the [React Compiler Rust port](https://github.com/react/react/pull/36173) and somewhere in the middle of TypeScript’s Go Port and [Bun’s Rust port](https://bun.com/bun-unsafe-audit). It’s still too early to judge whether we could have embraced AI even more aggressively or we should be slightly slower in some areas, so we just want to present our story of principled decision making and use of AI agents in the world of rapidly changing engineering practices.

## Related

- [[プログラミング言語-記事索引]]
