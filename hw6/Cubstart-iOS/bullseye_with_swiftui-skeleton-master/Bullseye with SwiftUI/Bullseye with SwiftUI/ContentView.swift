//
//  ContentView.swift
//  Bullseye with SwiftUI
//
//  Created by Tony Hong on 2/17/22.
//

import SwiftUI

struct ContentView: View {
    @State private var number: Double = 50
    @State private var exactMode = false
    var body: some View {
        VStack() {
            HStack() {
                VStack() {
                    Text("High Score")
                    Text("0")
                }
                .padding(.leading, 20)
                .padding(.top, 20)
                Spacer()
                
                VStack() {
                    Text("Current Level")
                    Text("1")
                }
                .padding(.trailing, 20)
                .padding(.top, 20)
            }
            
            VStack {
                Text("Move the slider to:")
                    .padding()
                    .font(.system(size: 30))
                Text("25")
                    .padding()
                    .font(.system(size: 30))
                Slider(value: $number, in: 0...100)
                    .padding(.all)
                Button(action: {
                    // What to perform
                    print("Check")
                }) {
                    // How the button looks like
                    Text("Check")
                }
            }
            .padding(.all)
            Spacer()
            VStack {
                Text("Exact Mode?")
            }
            VStack {
                Toggle("Exact Mode?", isOn: $exactMode)
                if exactMode {
                    Text("Hello World!")
                }
                
            }
            .labelsHidden()
        }
    }
}
